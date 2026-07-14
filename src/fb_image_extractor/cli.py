import argparse
from .extractor import FacebookImageExtractor
from .instagram import InstagramImageExtractor


def main():
    parser = argparse.ArgumentParser(
        description="Extract all your Facebook photos before deleting your account"
    )
    parser.add_argument("--cred", default=".cred", help="Path to credentials file (default: .cred)")
    parser.add_argument("--brave", default="/usr/bin/brave-browser", help="Path to Brave browser binary")

    # Facebook options
    parser.add_argument("--include-profile-cover", action="store_true", help="Include profile and cover photos")
    parser.add_argument("--all-albums", action="store_true", help="Scrape every album, not just photos_by and photos_of")

    # Instagram options
    parser.add_argument("--instagram", type=str, help="Instagram username to scrape after Facebook")
    parser.add_argument("--instagram-dir", default="./instagram_photos", help="Save directory for Instagram photos")
    parser.add_argument("--instagram-sections", default=",tagged", help="Comma-separated sections to scrape (default: '',tagged)")
    parser.add_argument("--include-ig-avatars", action="store_true", help="Include small profile/thumbnail images")
    parser.add_argument("--instagram-only", action="store_true", help="Skip Facebook, only run Instagram")

    args = parser.parse_args()

    if not args.instagram_only:
        extractor = FacebookImageExtractor(cred_path=args.cred, brave_binary=args.brave)
        if args.include_profile_cover:
            extractor.skip_profile_cover = False
        if args.all_albums:
            extractor.scrape_all_albums = True
        extractor.run()
    else:
        extractor = FacebookImageExtractor(cred_path=args.cred, brave_binary=args.brave)
        extractor.login()

    if args.instagram:
        sections = [s.strip() for s in args.instagram_sections.split(",") if s.strip() or s == ""]
        # Handle empty string for main feed
        sections = ["" if s == '""' or s == "''" else s for s in sections]
        ig = InstagramImageExtractor(
            driver=extractor.driver,
            username=args.instagram,
            save_dir=args.instagram_dir,
            sections=sections,
            log_callback=extractor.log_callback,
            skip_profile_avatars=not args.include_ig_avatars,
        )
        ig.run()
