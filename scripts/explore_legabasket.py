"""Recon: log all network requests on legabasketfemminile.it pages to find
per-game JSON/API endpoints (DataProject platform often exposes game-center
JSON via blob storage or .asmx/.ashx endpoints)."""

from playwright.sync_api import sync_playwright

PAGES = [
    "https://www.legabasketfemminile.it/Competition.aspx?ID=313",
    "https://www.legabasketfemminile.it/Calendar.aspx?ID=313",
    "https://www.legabasketfemminile.it/PlayerStats.aspx?ID=313",
]

INTERESTING = [".json", ".asmx", ".ashx", "/api/", "blob.core.windows.net", "dataproject"]


def log_requests(url: str):
    print(f"\n=== {url} ===")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        seen = []
        page.on("request", lambda req: seen.append(req.url))
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)

        # Try to find and click something that looks like a match/boxscore link
        candidates = page.locator("a, [onclick]")
        count = min(candidates.count(), 200)
        hrefs = []
        for i in range(count):
            el = candidates.nth(i)
            href = el.get_attribute("href") or ""
            onclick = el.get_attribute("onclick") or ""
            text = (el.inner_text() or "").strip()
            if href or onclick:
                hrefs.append((text[:40], href, onclick[:80]))

        browser.close()

    print(f"-- {len(seen)} network requests captured --")
    interesting = [u for u in seen if any(k in u.lower() for k in INTERESTING)]
    if interesting:
        print("INTERESTING requests:")
        for u in interesting:
            print("  ", u)
    else:
        print("No obviously interesting (json/api/blob) requests found.")

    print(f"\n-- {len(hrefs)} links/onclick elements found (first 40) --")
    for text, href, onclick in hrefs[:40]:
        if href or onclick:
            print(f"  [{text}] href={href!r} onclick={onclick!r}")


if __name__ == "__main__":
    for url in PAGES:
        log_requests(url)
