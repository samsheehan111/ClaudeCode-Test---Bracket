"""
Fetches KCLS (King County Library System) eBook hold counts from BiblioCommons
for Oprah's Book Club and Reese's Book Club selections.

Writes kc-holds.json to the repo root, which kc-bookclub.html reads at page load.

Run locally:  python scripts/fetch_kc_holds.py
Run in CI:    via .github/workflows/update-kc-holds.yml (every 12 hours)
"""

import json
import re
import time
from datetime import datetime, timezone

import requests

# ── Book list ────────────────────────────────────────────────────────────────
BOOKS = [
    # Oprah 2024
    {"id": "o24-01", "title": "The Many Lives of Mama Love",    "author": "Lara Love Hardin",    "club": "oprah", "year": 2024},
    {"id": "o24-02", "title": "Long Island",                     "author": "Colm Toibin",         "club": "oprah", "year": 2024},
    {"id": "o24-03", "title": "Familiaris",                      "author": "David Wroblewski",    "club": "oprah", "year": 2024},
    {"id": "o24-04", "title": "Tell Me Everything",              "author": "Elizabeth Strout",    "club": "oprah", "year": 2024},
    {"id": "o24-05", "title": "From Here to the Great Unknown",  "author": "Lisa Marie Presley",  "club": "oprah", "year": 2024},
    {"id": "o24-06", "title": "Small Things Like These",         "author": "Claire Keegan",       "club": "oprah", "year": 2024},
    # Oprah 2025
    {"id": "o25-01", "title": "Dream State",                     "author": "Eric Puchner",        "club": "oprah", "year": 2025},
    {"id": "o25-02", "title": "The Tell",                        "author": "Amy Griffin",         "club": "oprah", "year": 2025},
    {"id": "o25-03", "title": "Matriarch",                       "author": "Tina Knowles",        "club": "oprah", "year": 2025},
    {"id": "o25-04", "title": "The Emperor of Gladness",         "author": "Ocean Vuong",         "club": "oprah", "year": 2025},
    {"id": "o25-05", "title": "The River Is Waiting",            "author": "Wally Lamb",          "club": "oprah", "year": 2025},
    {"id": "o25-06", "title": "Culpability",                     "author": "Bruce Holsinger",     "club": "oprah", "year": 2025},
    {"id": "o25-07", "title": "Somebody's Fool",                 "author": "Richard Russo",       "club": "oprah", "year": 2025},
    {"id": "o25-08", "title": "A Guardian and a Thief",          "author": "Megha Majumdar",      "club": "oprah", "year": 2025},
    {"id": "o25-09", "title": "Some Bright Nowhere",             "author": "Ann Packer",          "club": "oprah", "year": 2025},
    # Reese 2024
    {"id": "r24-01", "title": "First Lie Wins",                  "author": "Ashley Elston",       "club": "reese", "year": 2024},
    {"id": "r24-02", "title": "City of Night Birds",             "author": "Juhea Kim",           "club": "reese", "year": 2024},
    {"id": "r24-03", "title": "Redwood Court",                   "author": "DeLana Dameron",      "club": "reese", "year": 2024},
    {"id": "r24-04", "title": "Anita de Monte Laughs Last",      "author": "Xochitl Gonzalez",    "club": "reese", "year": 2024},
    {"id": "r24-05", "title": "Did You Hear About Kitty Karr",   "author": "Crystal Smith Paul",  "club": "reese", "year": 2024},
    {"id": "r24-06", "title": "The Unwedding",                   "author": "Ally Condie",         "club": "reese", "year": 2024},
    {"id": "r24-07", "title": "The Cliffs",                      "author": "J. Courtney Sullivan","club": "reese", "year": 2024},
    {"id": "r24-08", "title": "Slow Dance",                      "author": "Rainbow Rowell",      "club": "reese", "year": 2024},
    {"id": "r24-09", "title": "The Comfort of Crows",            "author": "Margaret Renkl",      "club": "reese", "year": 2024},
    {"id": "r24-10", "title": "Society of Lies",                 "author": "Lauren Ling Brown",   "club": "reese", "year": 2024},
    {"id": "r24-11", "title": "We Will Be Jaguars",              "author": "Nemonte Nenquimo",    "club": "reese", "year": 2024},
    # Reese 2025
    {"id": "r25-01", "title": "The Three Lives of Cate Kay",     "author": "Kate Fagan",          "club": "reese", "year": 2025},
    {"id": "r25-02", "title": "Isola",                           "author": "Allegra Goodman",     "club": "reese", "year": 2025},
    {"id": "r25-03", "title": "The Tell",                        "author": "Amy Griffin",         "club": "reese", "year": 2025},
    {"id": "r25-04", "title": "Broken Country",                  "author": "Clare Leslie Hall",   "club": "reese", "year": 2025},
    {"id": "r25-05", "title": "Great Big Beautiful Life",        "author": "Emily Henry",         "club": "reese", "year": 2025},
    {"id": "r25-06", "title": "The Phoenix Pencil Company",      "author": "Allison King",        "club": "reese", "year": 2025},
    {"id": "r25-07", "title": "Spectacular Things",              "author": "Beck Dorey-Stein",    "club": "reese", "year": 2025},
    {"id": "r25-08", "title": "Once Upon a Time in Dollywood",   "author": "Ashley Jordan",       "club": "reese", "year": 2025},
    {"id": "r25-09", "title": "The Heir Apparent",               "author": "Rebecca Armitage",    "club": "reese", "year": 2025},
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

# King County Library System BiblioCommons base URL
BASE_URL = "https://kcls.bibliocommons.com/v2/search"

# ── Patterns to find in the HTML ─────────────────────────────────────────────
RE_HOLDS  = re.compile(r"Holds?:\s*(\d+)\s*on\s*(\d+)\s+cop(?:y|ies)", re.IGNORECASE)
RE_AVAIL  = re.compile(r"copies available", re.IGNORECASE)
RE_HOOPLA = re.compile(r"available on hoopla", re.IGNORECASE)


def fetch_book(book: dict) -> dict:
    params = {
        "query": book["title"],
        "searchType": "keyword",
        "f_FORMAT": "EBOOK",
    }
    try:
        resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=20)
        print(f"  HTTP {resp.status_code}  {book['title']}")

        if resp.status_code != 200:
            return {"status": "error", "text": f"HTTP {resp.status_code}", "available": False}

        html = resp.text

        # Try __NEXT_DATA__ embedded JSON (Next.js SSR) — most reliable
        next_data_match = re.search(
            r'<script[^>]+id="__NEXT_DATA__"[^>]*>(.*?)</script>',
            html, re.DOTALL
        )
        if next_data_match:
            try:
                data = json.loads(next_data_match.group(1))
                hold_info = _parse_next_data(data, book["author"])
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
                "available": False,
                "text": f"Holds: {holds} on {copies} cop{'y' if copies == 1 else 'ies'}",
            }

        if RE_AVAIL.search(html):
            return {"status": "available", "text": "Available now", "available": True}

        if RE_HOOPLA.search(html) and "EBOOK LIBBY" not in html.upper():
            return {"status": "hoopla", "text": "Hoopla (unlimited)", "available": True}

        return {"status": "unknown", "text": "—", "available": False}

    except requests.RequestException as e:
        print(f"  ERROR: {e}")
        return {"status": "error", "text": "—", "available": False}


def _parse_next_data(data: dict, author: str) -> dict | None:
    """
    Walk the Next.js page props to find hold/availability info.
    BiblioCommons embeds catalog data under pageProps → searchResults → entities.
    Prefers results whose contributor/author field matches the expected author.
    """
    try:
        entities = (
            data["props"]["pageProps"]
            .get("searchResults", {})
            .get("entities", {})
        )
        if not entities:
            return None

        best = None
        author_lower = author.lower()

        for entity in entities.values():
            if not isinstance(entity, dict):
                continue

            # Try to match by author to avoid returning wrong book
            contributors = entity.get("briefInfo", {}).get("contributors", [])
            if contributors:
                contrib_text = " ".join(
                    c.get("name", "") for c in contributors if isinstance(c, dict)
                ).lower()
                if author_lower.split()[0] not in contrib_text:
                    continue  # skip — wrong author

            availability = entity.get("availability", {})
            holds_count  = availability.get("holdsCount")
            copies_count = availability.get("totalCopies") or availability.get("copiesCount")
            avail_copies = availability.get("availableCopies", 0)

            if holds_count is None or copies_count is None:
                continue

            result = {
                "holds":  holds_count,
                "copies": copies_count,
            }
            if avail_copies and avail_copies > 0:
                result.update({
                    "status":    "available",
                    "available": True,
                    "text":      f"Available ({holds_count} holds, {copies_count} copies)",
                })
            else:
                result.update({
                    "status":    "holds",
                    "available": False,
                    "text":      f"Holds: {holds_count} on {copies_count} cop{'y' if copies_count == 1 else 'ies'}",
                })

            # Prefer a result with more data; stop on first strong author match
            best = result
            if author_lower.split()[0] in contrib_text:
                break

        return best

    except (KeyError, TypeError, AttributeError):
        pass
    return None


def main():
    print(f"Fetching KCLS eBook hold counts for {len(BOOKS)} books…\n")
    results = {}

    for book in BOOKS:
        results[book["id"]] = fetch_book(book)
        time.sleep(1.5)  # be polite to the KCLS server (~53s total)

    output = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "books":   results,
    }

    out_path = "kc-holds.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    statuses = [v["status"] for v in results.values()]
    print(f"\nDone! Written to {out_path}")
    print(f"  holds:     {statuses.count('holds')}")
    print(f"  available: {statuses.count('available')}")
    print(f"  hoopla:    {statuses.count('hoopla')}")
    print(f"  unknown:   {statuses.count('unknown')}")
    print(f"  error:     {statuses.count('error')}")


if __name__ == "__main__":
    main()
