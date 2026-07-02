import re
from playwright.sync_api import sync_playwright

URL = "https://www.legabasketfemminile.it/Calendar.aspx?ID=313"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    reqs = []
    page.on("request", lambda r: reqs.append(r.url))
    page.goto(URL, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(1000)

    before = len(reqs)
    page.click("a[title='Play Off']")
    page.wait_for_timeout(3000)
    after_reqs = reqs[before:]

    html = page.content()
    browser.close()

with open("scripts/_calendar_313_playoff.html", "w", encoding="utf-8") as f:
    f.write(html)

print("New requests after clicking Play Off tab:")
for u in after_reqs:
    print("  ", u)

mids = sorted(set(int(m) for m in re.findall(r"MatchStats\.aspx\?ID=313&amp;MID=(\d+)", html)))
print(f"\nMIDs found after click: {len(mids)}")
print(mids[:20])
