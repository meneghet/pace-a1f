"""Recon Serie B femminile on romagnasport.com: find real match-detail URL
pattern from the girone results page, then inspect one real tabellino."""

import re
import time
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (research script - pace analysis)"}

LIST_URL = "https://www.romagnasport.com/tuttobasket/classifica.php?gir=597&anno=2025"

resp = requests.get(LIST_URL, headers=HEADERS, timeout=15)
resp.raise_for_status()
html = resp.text
print(f"list page length: {len(html)}")

with open("scripts/explore/_serieb_list.html", "w", encoding="utf-8") as f:
    f.write(html)

soup = BeautifulSoup(html, "html.parser")
links = soup.find_all("a", href=True)
print(f"total <a> tags: {len(links)}")

candidates = set()
for a in links:
    href = a["href"]
    if any(k in href.lower() for k in ["partita", "tabellino", "match", "gara", "scheda"]):
        candidates.add(href)

print("\ncandidate match-detail hrefs:")
for c in sorted(candidates)[:30]:
    print("  ", c)

if not candidates:
    print("\nNo obvious match-detail links found by keyword. Dumping all unique href patterns (first 60):")
    uniq = sorted(set(a["href"] for a in links))
    for u in uniq[:60]:
        print("  ", u)
