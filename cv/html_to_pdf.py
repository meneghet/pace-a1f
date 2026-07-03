"""One-off: render a self-contained HTML file to PDF (and optionally a PNG
preview) using headless Chromium via Playwright. Not part of the pace
pipeline.
"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


def render(html_path: str, pdf_path: str, png_path: str | None = None):
    html_path = Path(html_path).resolve()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_path.as_uri())
        page.pdf(path=pdf_path, format="A4", print_background=True,
                 margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        if png_path:
            page.set_viewport_size({"width": 794, "height": 1123})
            page.screenshot(path=png_path, full_page=True)
        browser.close()
    print(f"Wrote {pdf_path}" + (f" and {png_path}" if png_path else ""))


if __name__ == "__main__":
    html_path = sys.argv[1]
    pdf_path = sys.argv[2] if len(sys.argv) > 2 else str(Path(html_path).with_suffix(".pdf"))
    png_path = sys.argv[3] if len(sys.argv) > 3 else None
    render(html_path, pdf_path, png_path)
