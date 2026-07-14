# 🔥 Meta Personal Data Collector

**Fuck Meta.**

This tool exists so you can grab every photo you ever uploaded or were tagged in - and then **delete your account and never look back**.

Facebook and Instagram treat us like a regular paycheck. We're not users, we're product. Every scroll, every like, every moment of envy - engineered to keep us hooked so they can sell our attention to the highest bidder. The amount of paid content, the influencer circus, the psychological manipulation of watching everyone have fun while you're just living your own life - it's reached a point where I genuinely can't stand being on their platforms.

It was cool a few years ago. It's not cool anymore.

**Burn it. Flip them off. Leave.**

---

> **Built on the work of [MariyaSha](https://github.com/MariyaSha/WebscrapingFacebook)** -  
> the original Facebook scraper this project was forked from. Thank you!

## How it works

1. Opens Brave (or Chrome) via Selenium
2. Logs into Facebook, visits your `photos_by` and `photos_of` (or all albums)
3. Scrolls continuously until every photo is loaded - goes back through your entire history
4. Visits each photo page, extracts the full-resolution image URL
5. Optionally skips profile pictures and cover photos
6. If Instagram is configured: switches tabs, scrapes both your main feed and tagged photos
7. Handles Instagram carousels (multi-image posts) - clicks through all slides
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

## 🔒 Privacy

**Your credentials never leave your machine.**

This tool uses [Selenium](https://www.selenium.dev/) to automate **your own browser** -
it opens Facebook's real login page and types your credentials there, the same way you
would manually. It does **not**:

- ❌ Send your password to any server besides Facebook/Instagram
- ❌ Phone home, call any API, or track usage
- ❌ Store or cache credentials beyond the current run

When using the web GUI (`streamlit run`), credentials are written to a local
`.cred_streamlit` file and deleted in a `finally` block as soon as the extraction
finishes. When using the CLI (`fb-extract`), credentials are read from `.cred`
(which is git-ignored) and passed directly to Selenium.

> The full source is at `src/fb_image_extractor/` - audit it yourself.

## Development

```bash
uv sync              # install deps
uv run pytest        # run tests
uv build             # build wheel
```
