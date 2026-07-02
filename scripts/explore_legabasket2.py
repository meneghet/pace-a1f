"""Dump full rendered HTML of Calendar/Competition pages and search for
match-detail link patterns (any href/onclick containing common game-related
keywords), plus print a chunk of the raw table markup around match rows."""

import re
from playwright.sync_api import sync_playwright

URL = "https://www.legabasketfemminile.it/Calendar.aspx?ID=313"

KEYWORDS = ["match", "game", "box", "report", "scheda", "tabellino", "gara"]

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(URL, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(1500)
    html = page.content()
    browser.close()

print(f"HTML length: {len(html)}")

# find all href/onclick occurrences case-insensitively containing keywords
for kw in KEYWORDS:
    matches = set(re.findall(rf'(?:href|onclick)="([^"]*{kw}[^"]*)"', html, re.IGNORECASE))
    if matches:
        print(f"\n--- matches for keyword '{kw}' ---")
        for m in list(matches)[:20]:
            print("  ", m)

# print a snippet around the word "vs" or a score pattern like "72 - 68" to see a match row's real markup
score_match = re.search(r'\d{2,3}\s*-\s*\d{2,3}', html)
if score_match:
    start = max(0, score_match.start() - 800)
    end = min(len(html), score_match.end() + 800)
    print("\n--- snippet around first score pattern ---")
    print(html[start:end])
else:
    print("\nNo score pattern found in HTML at all (page may render scores via JS/images or not show them yet).")
