"""
Fetches cover images and ratings from Google Books API for each book in books.json.
Updates books.json with working cover URLs and real ratings.

Run: python scripts/update_books_data.py
"""

import json
import time
import urllib.request
import urllib.parse

BOOKS_JSON = "books.json"

def fetch_google_books(title, author):
    query = f"intitle:{title} inauthor:{author}"
    url = "https://www.googleapis.com/books/v1/volumes?q=" + urllib.parse.quote(query) + "&maxResults=1"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
        items = data.get("items", [])
        if not items:
            return None
        info = items[0]["volumeInfo"]
        cover = None
        if "imageLinks" in info:
            # Use the largest available image, upgrade to https
            cover = info["imageLinks"].get("extraLarge") or info["imageLinks"].get("large") or info["imageLinks"].get("medium") or info["imageLinks"].get("thumbnail")
            if cover:
                cover = cover.replace("http://", "https://")
                # Request larger image
                cover = cover.replace("zoom=1", "zoom=3").replace("&edge=curl", "")
        rating = info.get("averageRating")
        ratings_count = info.get("ratingsCount")
        return {"cover": cover, "rating": rating, "ratings_count": ratings_count, "title_found": info.get("title")}
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

def main():
    with open(BOOKS_JSON) as f:
        books = json.load(f)

    for book in books:
        print(f"Fetching: {book['title']}...")
        result = fetch_google_books(book["title"], book["author"])
        if result:
            print(f"  Found: {result['title_found']}")
            if result["cover"]:
                book["cover"] = result["cover"]
                print(f"  Cover: {result['cover'][:60]}...")
            else:
                print(f"  No cover found, keeping existing")
            if result["rating"] is not None:
                book["rating"] = result["rating"]
                print(f"  Rating: {result['rating']}")
            else:
                print(f"  No rating found, keeping existing")
            if result["ratings_count"] is not None:
                book["reviews"] = result["ratings_count"]
                print(f"  Reviews: {result['ratings_count']}")
            else:
                print(f"  No review count found, keeping existing")
        else:
            print(f"  Not found in Google Books")
        time.sleep(0.5)  # be polite

    with open(BOOKS_JSON, "w") as f:
        json.dump(books, f, indent=2, ensure_ascii=False)
    print("\nDone! books.json updated.")

if __name__ == "__main__":
    main()
