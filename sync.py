"""Conservative public eMOL scraper: never invent entries or overwrite valid data on failure."""
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

SOURCE = "https://emol.ro/targucarbunesti-gj/registru-dp/"
OUTPUT = Path("data/dispozitii.json")
NUMBER = re.compile(r"(?:Nr\.?\s*)?(\d{1,5})\s*/\s*(\d{1,2}[./-]\d{1,2}[./-]20\d{2})", re.I)

def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    # Diagnostics for public registry markup; no credentials or personal data logged.
    rows = soup.select("table tbody tr")
    if not rows:
        print("eMOL DIAGNOSTIC: title=", soup.title.get_text(" ", strip=True)[:160] if soup.title else "(none)", flush=True)
        print("eMOL DIAGNOSTIC: tables=", len(soup.select("table")), "rows=", len(soup.select("tr")), "iframes=", len(soup.select("iframe")), flush=True)
        print("eMOL DIAGNOSTIC: links=", len(soup.select("a[href]")), flush=True)
        for a in soup.select("a[href]")[:12]:
            print("eMOL LINK:", repr(a.get_text(" ", strip=True)[:90]), repr(a.get("href", "")[:180]), flush=True)
        for frame in soup.select("iframe[src]")[:5]:
            print("eMOL FRAME:", repr(frame.get("src", "")[:220]), flush=True)
        print("eMOL DIAGNOSTIC: body preview=", repr(soup.body.get_text(" ", strip=True)[:900]) if soup.body else "(none)", flush=True)

    if not rows:
        raise RuntimeError("Nu există rânduri de registru în HTML-ul public; necesită adaptarea selectorilor")
    items = []
    for row in rows:
        text = row.get_text(" ", strip=True)
        match = NUMBER.search(text)
        if not match:
            continue
        number, date = match.groups()
        links = []
        for a in row.select("a[href]"):
            url = urljoin(SOURCE, a.get("href", ""))
            parsed = urlparse(url)
            if parsed.netloc == "emol.ro" and "/targucarbunesti-gj/" in parsed.path and url != SOURCE and not url.endswith("#!"):
                links.append(url)
        if not links:
            continue
        cells = [c.get_text(" ", strip=True) for c in row.select("td")]
        title = next((c for c in cells if len(c) > 24 and not NUMBER.fullmatch(c)), "")
        if not title:
            continue
        items.append({"number": int(number), "date": date.replace("/", ".").replace("-", "."), "title": title[:1000], "url": links[0]})
    unique = {(x["number"], x["date"]): x for x in items}
    def key(x):
        try:
            return datetime.strptime(x["date"], "%d.%m.%Y"), x["number"]
        except ValueError:
            return datetime.min, x["number"]
    result = sorted(unique.values(), key=key, reverse=True)[:10]
    if not result:
        raise RuntimeError("Nu au fost identificate dispoziții publice verificabile cu link individual")
    return result

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(locale="ro-RO", viewport={"width": 1440, "height": 1000})
        page.goto(SOURCE, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(5000)
        html = page.content()
        browser.close()
    items = parse(html)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({"source": SOURCE, "updated_at": datetime.now(timezone.utc).isoformat(), "items": items, "status": "verified"}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Au fost verificate {len(items)} dispoziții")

if __name__ == "__main__":
    main()
