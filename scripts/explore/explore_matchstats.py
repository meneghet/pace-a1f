"""Inspect MatchStats.aspx?ID=313&MID=<id> to see if per-game team box score
(FGA, FTA, offensive rebounds, turnovers) is available."""

from playwright.sync_api import sync_playwright

URL = "https://www.legabasketfemminile.it/MatchStats.aspx?ID=313&MID=53431"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(URL, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(2000)
    html = page.content()
    text = page.inner_text("body")
    browser.close()

with open("scripts/explore/_matchstats_sample.html", "w", encoding="utf-8") as f:
    f.write(html)

with open("scripts/explore/_matchstats_sample.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("done, saved html + text")
