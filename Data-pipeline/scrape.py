import csv
import time
import requests
from bs4 import BeautifulSoup

BASE = "https://books.toscrape.com/"

CATEGORIES = {
    "Travel": "catalogue/category/books/travel_2/index.html",
    "Mystery": "catalogue/category/books/mystery_3/index.html",
    "Historical Fiction": "catalogue/category/books/historical-fiction_4/index.html",
    "Science Fiction": "catalogue/category/books/science-fiction_16/index.html",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (educational scraping exercise; books.toscrape.com)"}


def get_soup(url):
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def scrape_category(category_name, start_path):
    """Walk every paginated page of one category, yielding one dict per book."""
    url = BASE + start_path
    rows = []
    while url:
        soup = get_soup(url)
        for article in soup.select("article.product_pod"):
            title = article.h3.a["title"]
            price = article.select_one("p.price_color").get_text(strip=True)
            rating_classes = article.select_one("p.star-rating")["class"]
            star_rating_text = [c for c in rating_classes if c != "star-rating"][0]
            availability = article.select_one("p.instock.availability").get_text(strip=True)
            rows.append({
                "title": title,
                "price": price,
                "star_rating": star_rating_text,
                "availability": availability,
                "category": category_name,
            })
        next_link = soup.select_one("li.next a")
        url = url.rsplit("/", 1)[0] + "/" + next_link["href"] if next_link else None
        time.sleep(0.3)
    return rows


def main():
    all_rows = []
    for category_name, start_path in CATEGORIES.items():
        cat_rows = scrape_category(category_name, start_path)
        print(f"{category_name}: {len(cat_rows)} books")
        all_rows.extend(cat_rows)

    print(f"\nTotal books scraped: {len(all_rows)}")
    assert len(all_rows) >= 60, "Dataset must have at least 60 books"

    with open("raw_books.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "price", "star_rating", "availability", "category"])
        writer.writeheader()
        writer.writerows(all_rows)
    print("Saved -> raw_books.csv")


if __name__ == "__main__":
    main()
