import time
from pathlib import Path
from dotenv import dotenv_values
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class FacebookImageExtractor:
    ALBUMS = ["photos_by", "photos_of"]

    def __init__(self, cred_path=".cred", brave_binary="/usr/bin/brave-browser", log_callback=None):
        creds = dotenv_values(cred_path)
        self.username = creds.get("FB_USERNAME")
        self.password = creds.get("FB_PASSWORD")
        self.profile = creds.get("FB_PROFILE")
        self.save_dir = Path(creds.get("SAVE_DIR", "./downloaded_photos"))
        self.skip_profile_cover = creds.get("SKIP_PROFILE_COVER", "true").lower() == "true"
        self.scrape_all_albums = creds.get("SCRAPE_ALL_ALBUMS", "false").lower() == "true"
        self.brave_binary = brave_binary
        self.log_callback = log_callback
        self._driver = None
        self._images = []

    def log(self, msg):
        if self.log_callback:
            self.log_callback(msg)
        else:
            print(msg)

    def _init_driver(self):
        opts = Options()
        opts.binary_location = self.brave_binary
        prefs = {"profile.default_content_setting_values.notifications": 2}
        opts.add_experimental_option("prefs", prefs)
        self._driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=opts
        )
        return self._driver

    @property
    def driver(self):
        if self._driver is None:
            self._init_driver()
        return self._driver

    @driver.setter
    def driver(self, d):
        self._driver = d

    def login(self):
        self.driver.get("https://www.facebook.com")
        wait = WebDriverWait(self.driver, 15)
        username_el = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']")))
        password_el = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='pass']")))
        username_el.clear()
        username_el.send_keys(self.username)
        password_el.clear()
        password_el.send_keys(self.password)
        login_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[aria-label='Log In']")))
        login_btn.click()
        time.sleep(5)

    def discover_albums(self):
        self.driver.get(f"https://www.facebook.com/{self.profile}/photos/albums")
        time.sleep(5)
        anchors = self.driver.find_elements(By.TAG_NAME, "a")
        albums = set()
        for a in anchors:
            href = a.get_attribute("href")
            if href and f"/{self.profile}/albums/" in href:
                album_id = href.split("/albums/")[-1].split("/")[0]
                if album_id.isdigit():
                    albums.add(album_id)
        result = sorted(albums)
        self.log(f"  Found {len(result)} albums")
        return result

    def _collect_photo_links(self, album_or_id):
        if str(album_or_id).isdigit():
            url = f"https://www.facebook.com/album.php?profile_id={self.profile}&id={album_or_id}"
        else:
            url = f"https://www.facebook.com/{self.profile}/{album_or_id}/"
        self.driver.get(url)
        time.sleep(5)
        seen = set()
        no_new = 0
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            anchors = self.driver.find_elements(By.TAG_NAME, "a")
            links = [
                a.get_attribute("href")
                for a in anchors
                if a.get_attribute("href") and a.get_attribute("href").startswith("https://www.facebook.com/photo")
            ]
            new = {l for l in links if l not in seen}
            if not new:
                no_new += 1
                if no_new >= 3:
                    break
            else:
                no_new = 0
                seen.update(new)
        self.log(f"  Found {len(seen)} unique photo links")
        return list(seen)

    def _extract_image_src(self, link):
        self.driver.get(link)
        time.sleep(3)
        imgs = self.driver.find_elements(By.TAG_NAME, "img")
        for img in imgs:
            alt = (img.get_attribute("alt") or "").lower()
            if self.skip_profile_cover and ("profile" in alt or "cover" in alt):
                return None
        for img in imgs:
            src = img.get_attribute("src")
            if src and "scontent" in src:
                return src
        for img in imgs:
            src = img.get_attribute("src")
            if src and not src.startswith("data:"):
                return src
        return None

    def scrape(self):
        self._images = []
        albums = []
        if self.scrape_all_albums:
            albums = self.discover_albums()
        else:
            albums = list(self.ALBUMS)
        for album in albums:
            self.log(f"\n--- Album: {album} ---")
            links = self._collect_photo_links(album)
            for idx, link in enumerate(links):
                src = self._extract_image_src(link)
                if src:
                    self._images.append(src)
                    self.log(f"  [{idx+1}/{len(links)}] Got: {src[-40:]}")
                else:
                    self.log(f"  [{idx+1}/{len(links)}] Skipped")
        self.log(f"\nCollected {len(self._images)} image URLs")
        return self._images

    def download(self):
        self.save_dir.mkdir(parents=True, exist_ok=True)
        count = 0
        for url in self._images:
            if not url or url.startswith("data:") or "static.xx.fbcdn.net" in url:
                continue
            resp = requests.get(url, timeout=30)
            ext = ".jpg"
            if resp.headers.get("content-type", "").endswith("png"):
                ext = ".png"
            path = self.save_dir / f"{count}{ext}"
            with open(path, "wb") as f:
                f.write(resp.content)
            count += 1
        self.log(f"Downloaded {count} photos to {self.save_dir}")
        return count

    def run(self):
        try:
            self.login()
            self.scrape()
            self.download()
        finally:
            if self._driver:
                self._driver.quit()
