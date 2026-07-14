import time
from pathlib import Path
import requests

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class InstagramImageExtractor:
    SECTIONS = ["", "tagged"]

    def __init__(self, driver, username, save_dir="./instagram_photos", log_callback=None, sections=None, skip_profile_avatars=True):
        self.driver = driver
        self.username = username
        self.save_dir = Path(save_dir)
        self.log_callback = log_callback
        self.sections = sections or list(self.SECTIONS)
        self.skip_profile_avatars = skip_profile_avatars
        self._images = []

    def log(self, msg):
        if self.log_callback:
            self.log_callback(msg)
        else:
            print(msg)

    def _switch_to_ig_tab(self):
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            if "instagram.com" in self.driver.current_url:
                self.log(f"  Switched to Instagram tab: {self.driver.current_url}")
                return True
        return False

    def _navigate_to(self, section=""):
        path = f"https://www.instagram.com/{self.username}/{section}"
        self.driver.get(path)
        time.sleep(5)

    def _collect_post_links(self):
        seen = set()
        no_new = 0
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(4)
            anchors = self.driver.find_elements(By.TAG_NAME, "a")
            links = [
                a.get_attribute("href")
                for a in anchors
                if a.get_attribute("href") and "/p/" in a.get_attribute("href")
            ]
            new = {l.split("?")[0] for l in links if l.split("?")[0] not in seen}
            if not new:
                no_new += 1
                if no_new >= 3:
                    break
            else:
                no_new = 0
                seen.update(new)
        result = sorted(seen)
        self.log(f"  Found {len(result)} posts")
        return result

    def _collect_large_images(self, urls):
        for img in self.driver.find_elements(By.TAG_NAME, "img"):
            src = img.get_attribute("src")
            if not src or "cdninstagram.com" not in src:
                continue
            if self.skip_profile_avatars:
                w = img.size.get("width", 0)
                h = img.size.get("height", 0)
                if w < 400 or h < 400:
                    continue
            urls.add(src)

    def _extract_post_images(self, post_url):
        self.driver.get(post_url)
        time.sleep(3)
        urls = set()

        self._collect_large_images(urls)

        # Click through carousel arrows to get slides 2,3,4...
        for _ in range(15):
            try:
                btn = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next']")
                if not btn.is_displayed():
                    break
                btn.click()
                time.sleep(1.5)
                self._collect_large_images(urls)
            except Exception:
                break

        return list(urls)

    def scrape(self):
        self._images = []
        if not self._switch_to_ig_tab():
            self.log("  Instagram tab not found, navigating directly...")
        for section in self.sections:
            label = section if section else "posts"
            self.log(f"\n--- Section: {label} ---")
            self._navigate_to(section)
            posts = self._collect_post_links()
            for idx, post_url in enumerate(posts):
                srcs = self._extract_post_images(post_url)
                for s in srcs:
                    self._images.append(s)
                self.log(f"  [{idx+1}/{len(posts)}] Post: {len(srcs)} image(s)")
        self.log(f"\nCollected {len(self._images)} Instagram images")
        return self._images

    def download(self):
        self.save_dir.mkdir(parents=True, exist_ok=True)
        count = 0
        for url in self._images:
            try:
                resp = requests.get(url, timeout=30)
                ext = ".jpg"
                ct = resp.headers.get("content-type", "")
                if "png" in ct:
                    ext = ".png"
                elif "webp" in ct:
                    ext = ".webp"
                path = self.save_dir / f"{count}{ext}"
                with open(path, "wb") as f:
                    f.write(resp.content)
                count += 1
            except Exception as e:
                self.log(f"    Failed: {url[:60]} — {e}")
        self.log(f"Downloaded {count} Instagram photos to {self.save_dir}")
        return count

    def run(self):
        self.scrape()
        self.download()
