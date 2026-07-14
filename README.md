# Facebook & Instagram Image Extractor

Extract every photo you've ever uploaded or been tagged in — before you delete your accounts.  
Downloads your entire photo library (uploaded + tagged) from both Facebook and Instagram.

> **Built on the work of [MariyaSha](https://github.com/MariyaSha/WebscrapingFacebook)** —  
> the original Facebook scraper this project was forked from. Thank you!

## How it works

1. Opens Brave (or Chrome) via Selenium
2. Logs into Facebook, visits your `photos_by` and `photos_of` (or all albums)
3. Scrolls continuously until every photo is loaded — goes back through your entire history
4. Visits each photo page, extracts the full-resolution image URL
5. Optionally skips profile pictures and cover photos
6. If Instagram is configured: switches tabs, scrapes both your main feed and tagged photos
7. Handles Instagram carousels (multi-image posts) — clicks through all slides
8. Filters out avatars, thumbnails, and "More posts" suggestions by image size
9. Downloads everything to your chosen directory

## Quick start

### 1. Install

```bash
uv sync
```

Installs all dependencies in one shot (Selenium, Streamlit, requests, etc.).

### 2. Set up credentials

```bash
cp .cred.example .cred
# Then edit .cred with your Facebook login details
```

### 3. Run

**Command line (recommended):**

```bash
# Facebook only
uv run fb-extract

# Facebook + Instagram
uv run fb-extract --instagram your_ig_username

# Instagram only (if you're already logged into Facebook in the browser)
uv run fb-extract --instagram-only --instagram your_ig_username
```

**Web GUI (point-and-click):**

```bash
uv run streamlit run src/fb_image_extractor/app.py
```

Then open the URL shown in the terminal (usually `http://localhost:8501`) and fill in the form.

### All CLI options

```
--cred PATH               Credentials file (default: .cred)
--brave PATH              Brave browser binary (default: /usr/bin/brave-browser)

--include-profile-cover   Include profile and cover photos
--all-albums              Scrape every album, not just photos_by/photos_of

--instagram USER          Instagram username to scrape after Facebook
--instagram-dir DIR       Save directory for Instagram photos (default: ./instagram_photos)
--instagram-sections S    Sections: main feed, tagged, or both (default: ",tagged")
--include-ig-avatars      Include small profile/thumbnail images
--instagram-only          Skip Facebook, scrape Instagram only
```

## Credentials file (`.cred`)

```
FB_USERNAME=you@example.com
FB_PASSWORD=your_password
FB_PROFILE=your.profile.name
SAVE_DIR=./downloaded_photos
SKIP_PROFILE_COVER=true
SCRAPE_ALL_ALBUMS=false
```

`.cred` is git-ignored. Use `.cred.example` as a template.

## Development

```bash
uv sync              # install deps
uv run pytest        # run tests
uv build             # build wheel
```
