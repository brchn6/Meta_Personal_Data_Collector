import streamlit as st
from pathlib import Path
from fb_image_extractor.extractor import FacebookImageExtractor
from fb_image_extractor.instagram import InstagramImageExtractor


def run():
    st.set_page_config(page_title="Facebook Image Extractor", page_icon="📸", layout="wide")
    st.title("🔥 Meta Personal Data Collector")
    st.markdown("Grab your photos, then **delete your account and never look back**.")

    # ── Privacy reassurance ──────────────────────────────────────────
    with st.expander("🔒 Privacy — how your credentials are used", expanded=True):
        st.markdown(
            """
            **Your credentials never leave this machine.** Here's exactly what happens:

            1. You type your Facebook (and optionally Instagram) login into **this form**.
            2. The script saves them temporarily to a local `.cred_streamlit` file
               (deleted as soon as the run finishes — see the `finally` block in the code).
            3. Selenium opens **your own browser** (Brave/Chrome) and types them into
               **Facebook's own login page** — just as if you typed them yourself.
            4. No data is sent to any server other than Facebook/Instagram themselves.
               No external API, no phone-home, no tracking.

            👉 The full source is at `src/fb_image_extractor/` — read it, build from it,
               or audit the network tab in your browser to verify zero unexpected traffic.
            """
        )
    # ─────────────────────────────────────────────────────────────────

    with st.sidebar:
        st.header("Facebook")
        fb_username = st.text_input("FB email / username", key="fb_user")
        fb_password = st.text_input("FB password", type="password", key="fb_pass")
        fb_profile = st.text_input("FB profile name (e.g. BarCo840)", key="fb_prof")
        fb_save = st.text_input("FB save directory", value="./downloaded_photos", key="fb_save")
        fb_skip_pc = st.checkbox("Skip profile & cover photos", value=True, key="fb_skip")
        fb_all_albums = st.checkbox("Scrape ALL albums (not just photos_by/of)", value=False, key="fb_all")
        fb_brave = st.text_input("Brave binary path", value="/usr/bin/brave-browser", key="fb_brave")

        st.header("Instagram")
        ig_enabled = st.checkbox("Also scrape Instagram", value=False, key="ig_on")
        ig_username = st.text_input("IG username (e.g. barco42)", key="ig_user", disabled=not ig_enabled)
        ig_save = st.text_input("IG save directory", value="./instagram_photos", key="ig_save", disabled=not ig_enabled)
        ig_sections = st.text_input("IG sections (comma-separated)", value=",tagged", key="ig_sec", disabled=not ig_enabled,
                                    help="empty string = main feed, 'tagged' = photos of you")
        ig_skip_avatars = st.checkbox("Skip small images (<400px)", value=True, key="ig_skip", disabled=not ig_enabled)

        start = st.button("🚀 Start Extraction", type="primary", use_container_width=True)

    log_box = st.empty()

    if not start:
        st.info("Fill in your credentials in the sidebar and click **Start Extraction**.")
        st.stop()

    if not fb_username or not fb_password or not fb_profile:
        st.error("Facebook username, password, and profile name are required.")
        st.stop()

    cred_path = Path(".cred_streamlit")
    cred_path.write_text(
        f"FB_USERNAME={fb_username}\n"
        f"FB_PASSWORD={fb_password}\n"
        f"FB_PROFILE={fb_profile}\n"
        f"SAVE_DIR={fb_save}\n"
        f"SKIP_PROFILE_COVER={'true' if fb_skip_pc else 'false'}\n"
    )

    logs = []

    def log_callback(msg):
        logs.append(msg)
        log_box.code("\n".join(logs[-50:]), language="")

    status = st.status("Starting...", expanded=True)

    try:
        status.write("Initializing browser...")
        ext = FacebookImageExtractor(cred_path=str(cred_path), brave_binary=fb_brave, log_callback=log_callback)
        if fb_all_albums:
            ext.scrape_all_albums = True

        status.write("Logging into Facebook...")
        ext.login()
        status.write("Logged in. Scraping photo links...")

        ext.scrape()
        status.write(f"Scraping done. {len(ext._images)} URLs. Downloading...")

        fb_count = ext.download()
        status.write(f"Facebook: {fb_count} photos saved to {fb_save}")

        if ig_enabled and ig_username:
            sections = [s.strip() for s in ig_sections.split(",") if s.strip() or s == ""]
            status.write("Starting Instagram scraping...")
            ig = InstagramImageExtractor(
                driver=ext.driver,
                username=ig_username,
                save_dir=ig_save,
                sections=sections,
                log_callback=log_callback,
                skip_profile_avatars=ig_skip_avatars,
            )
            ig.scrape()
            ig_count = ig.download()
            status.write(f"Instagram: {ig_count} photos saved to {ig_save}")
        else:
            ig_count = 0

        total = fb_count + ig_count
        status.update(label=f"✅ Done! Downloaded {total} photos total (FB: {fb_count}, IG: {ig_count})", state="complete", expanded=False)
        st.success(f"Downloaded {total} photos total — FB: {fb_count}, IG: {ig_count}")
        st.balloons()
    except Exception as e:
        status.update(label=f"❌ Error: {e}", state="error", expanded=True)
        st.exception(e)
    finally:
        if cred_path.exists():
            cred_path.unlink()


if __name__ == "__main__":
    run()
