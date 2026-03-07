"""
Fetches SFPL ebook hold counts from BiblioCommons for the book club tracker.
Writes holds.json to the repo root, which bookclub.html reads at page load.

Run locally:  python scripts/fetch_holds.py
Run in CI:    via .github/workflows/update-holds.yml
"""

import json
import re
import time
from datetime import datetime, timezone

import requests

# ── Book list — keep in sync with bookclub.html ──────────────────────────────
BOOKS = [
    # Oprah 2024
    {"id": "o24-01", "title": "The Many Lives of Mama Love",      "author": "Lara Love Hardin"},
    {"id": "o24-02", "title": "Long Island",                       "author": "Colm Toibin"},
    {"id": "o24-03", "title": "Familiaris",                        "author": "David Wroblewski"},
    {"id": "o24-04", "title": "Tell Me Everything",                "author": "Elizabeth Strout"},
    {"id": "o24-05", "title": "From Here to the Great Unknown",    "author": "Lisa Marie Presley"},
    {"id": "o24-06", "title": "Small Things Like These",           "author": "Claire Keegan"},
    # Oprah 2025
    {"id": "o25-01", "title": "Dream State",                       "author": "Eric Puchner"},
    {"id": "o25-02", "title": "The Tell",                          "author": "Amy Griffin"},
    {"id": "o25-03", "title": "Matriarch",                         "author": "Tina Knowles"},
    {"id": "o25-04", "title": "The Emperor of Gladness",           "author": "Ocean Vuong"},
    {"id": "o25-05", "title": "The River Is Waiting",              "author": "Wally Lamb"},
    {"id": "o25-06", "title": "Culpability",                       "author": "Bruce Holsinger"},
    {"id": "o25-07", "title": "Somebody's Fool",                   "author": "Richard Russo"},
    {"id": "o25-08", "title": "A Guardian and a Thief",            "author": "Megha Majumdar"},
    {"id": "o25-09", "title": "Some Bright Nowhere",               "author": "Ann Packer"},
    # Reese 2024
    {"id": "r24-01", "title": "First Lie Wins",                    "author": "Ashley Elston"},
    {"id": "r24-02", "title": "City of Night Birds",               "author": "Juhea Kim"},
    {"id": "r24-03", "title": "Redwood Court",                     "author": "DeLana Dameron"},
    {"id": "r24-04", "title": "Anita de Monte Laughs Last",        "author": "Xochitl Gonzalez"},
    {"id": "r24-05", "title": "Did You Hear About Kitty Karr",     "author": "Crystal Smith Paul"},
    {"id": "r24-06", "title": "The Unwedding",                     "author": "Ally Condie"},
    {"id": "r24-07", "title": "The Cliffs",                        "author": "J. Courtney Sullivan"},
    {"id": "r24-08", "title": "Slow Dance",                        "author": "Rainbow Rowell"},
    {"id": "r24-09", "title": "The Comfort of Crows",              "author": "Margaret Renkl"},
    {"id": "r24-10", "title": "Society of Lies",                   "author": "Lauren Ling Brown"},
    {"id": "r24-11", "title": "We Will Be Jaguars",                "author": "Nemonte Nenquimo"},
    # Reese 2025
    {"id": "r25-01", "title": "The Three Lives of Cate Kay",       "author": "Kate Fagan"},
    {"id": "r25-02", "title": "Isola",                             "author": "Allegra Goodman"},
    {"id": "r25-04", "title": "Broken Country",                    "author": "Clare Leslie Hall"},
    {"id": "r25-05", "title": "Great Big Beautiful Life",          "author": "Emily Henry"},
    {"id": "r25-06", "title": "The Phoenix Pencil Company",        "author": "Allison King"},
    {"id": "r25-07", "title": "Spectacular Things",                "author": "Beck Dorey-Stein"},
    {"id": "r25-08", "title": "Once Upon a Time in Dollywood",     "author": "Ashley Jordan"},
    {"id": "r25-09", "title": "The Heir Apparent",                 "author": "Rebecca Armitage"},
]

# ── HTTP headers that look like a real browser ───────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
}

BASE_URL = "https://sfpl.bibliocommons.com/v2/search"

# ── Patterns to find in the HTML ─────────────────────────────────────────────
RE_HOLDS    = re.compile(r"Holds?:\s*(\d+)\s*on\s*(\d+)\s+cop(?:y|ies)", re.IGNORECASE)
RE_AVAIL    = re.compile(r"copies available", re.IGNORECASE)
RE_HOOPLA   = re.compile(r"available on hoopla", re.IGNORECASE)


def fetch_book(book: dict) -> dict:
    query = f"{book['title']} {book['author']}"
    params = {
        "query": query,
        "searchType": "keyword",
        "f_FORMAT": "EBOOK",
    }
    try:
        resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=20)
        print(f"  HTTP {resp.status_code}  {book['title']}")

        if resp.status_code != 200:
            return {"status": "error", "text": f"HTTP {resp.status_code}"}

        html = resp.text

        # Try to pull __NEXT_DATA__ embedded JSON (Next.js SSR)
        # This is more structured and reliable than raw HTML regex
        next_data_match = re.search(
            r'<script[^>]+id="__NEXT_DATA__"[^>]*>(.*?)</script>',
            html, re.DOTALL
        )
        if next_data_match:
            try:
                data = json.loads(next_data_match.group(1))
                hold_info = _parse_next_data(data)
                if hold_info:
                    return hold_info
            except (json.JSONDecodeError, KeyError):
                pass

        # Fall back to regex on raw HTML
        holds_match = RE_HOLDS.search(html)
        if holds_match:
            holds  = int(holds_match.group(1))
            copies = int(holds_match.group(2))
            return {
                "status": "holds",
                "holds": holds,
                "copies": copies,
                "text": f"Holds: {holds} on {copies} cop{'y' if copies == 1 else 'ies'}",
                "available": False,
            }

        if RE_AVAIL.search(html):
            return {"status": "available", "text": "Available", "available": True}

        if RE_HOOPLA.search(html) and "EBOOK LIBBY" not in html.upper():
            # Only Hoopla available (unlimited, no holds)
            return {"status": "hoopla", "text": "Hoopla only", "available": True}

        # Found the page but couldn't parse availability
        return {"status": "unknown", "text": "—"}

    except requests.RequestException as e:
        print(f"  ERROR: {e}")
        return {"status": "error", "text": "—"}


def _parse_next_data(data: dict) -> dict | None:
    """
    Walk the Next.js page props to find hold/availability info.
    BiblioCommons embeds catalog data under pageProps → searchResults → entities.
    This is a best-effort parse; structure may change.
    """
    try:
        entities = (
            data["props"]["pageProps"]
            .get("searchResults", {})
            .get("entities", {})
        )
        if not entities:
            return None

        # Collect all entity values and look for hold info
        for entity in entities.values():
            if not isinstance(entity, dict):
                continue
            availability = entity.get("availability", {})
            holds_count  = availability.get("holdsCount")
            copies_count = availability.get("totalCopies") or availability.get("copiesCount")
            avail_copies = availability.get("availableCopies", 0)

            if holds_count is not None and copies_count is not None:
                if avail_copies > 0:
                    return {
                        "status": "available",
                        "holds": holds_count,
                        "copies": copies_count,
                        "available": True,
                        "text": f"Available ({holds_count} holds, {copies_count} copies)",
                    }
                return {
                    "status": "holds",
                    "holds": holds_count,
                    "copies": copies_count,
                    "available": False,
                    "text": f"Holds: {holds_count} on {copies_count} cop{'y' if copies_count == 1 else 'ies'}",
                }
    except (KeyError, TypeError, AttributeError):
        pass
    return None


def main():
    print(f"Fetching hold counts for {len(BOOKS)} books…\n")
    results = {}

    for book in BOOKS:
        results[book["id"]] = fetch_book(book)
        time.sleep(1.5)  # be polite — ~50s total for 33 books

    output = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "books": results,
    }

    out_path = "holds.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    # Summary
    statuses = [v["status"] for v in results.values()]
    print(f"\nDone! Written to {out_path}")
    print(f"  holds:     {statuses.count('holds')}")
    print(f"  available: {statuses.count('available')}")
    print(f"  hoopla:    {statuses.count('hoopla')}")
    print(f"  unknown:   {statuses.count('unknown')}")
    print(f"  error:     {statuses.count('error')}")


if __name__ == "__main__":
    main()
