#!/usr/bin/env python3
"""Render brochure/CIS-Tech-Consulting-Brochure.html to PDF via the
pre-installed Chromium (same Skia/PDF engine that made the original).

A4, zero margins, backgrounds on, waits for fonts + images to settle.
Output overwrites the repo-root CIS Tech Consulting Brochure.pdf.
"""
import pathlib, sys
from playwright.sync_api import sync_playwright

HTML = pathlib.Path("/home/user/ltm-core/brochure/CIS-Tech-Consulting-Brochure.html")
OUT  = pathlib.Path("/home/user/ltm-core/CIS Tech Consulting Brochure.pdf")
import glob as _glob
_cands = sorted(_glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"))
CHROMIUM = _cands[-1] if _cands else "/opt/pw-browsers/chromium/chrome-linux/chrome"

def main() -> int:
    with sync_playwright() as p:
        launch = {"args": ["--no-sandbox", "--font-render-hinting=none"]}
        exe = pathlib.Path(CHROMIUM)
        if exe.exists():
            launch["executable_path"] = str(exe)
        browser = p.chromium.launch(**launch)
        page = browser.new_page()
        page.goto(HTML.as_uri(), wait_until="networkidle", timeout=60000)
        # Give web fonts a beat to swap in
        try:
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(1200)
        except Exception:
            page.wait_for_timeout(1500)
        page.pdf(
            path=str(OUT),
            format="A4",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            prefer_css_page_size=True,
        )
        browser.close()
    size = OUT.stat().st_size
    print(f"  ✓ wrote {OUT.name}: {size//1024} KB")
    return 0

if __name__ == "__main__":
    sys.exit(main())
