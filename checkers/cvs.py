from curl_cffi import requests

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}


def check_stock(url: str) -> bool:
    """Return True if the CVS product page shows an in-stock signal."""
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            impersonate="chrome120",
            timeout=20,
        )
        print(f"  [CVS] {url} — HTTP {response.status_code}")
        if response.status_code != 200:
            print(f"  [CVS] Unexpected status, skipping.")
            return False

        html = response.text
        in_stock = (
            '"availability":"http://schema.org/InStock"' in html
            or ">Add to basket<" in html
        )
        print(f"  [CVS] In-stock signal found: {in_stock}")
        return in_stock
    except Exception as e:
        print(f"  [CVS] Error checking {url}: {e}")
        return False


if __name__ == "__main__":
    test_url = "https://www.cvs.com/shop/pokemon-trading-card-game-scarlet-violet-151-elite-trainer-box-prodid-714855"
    result = check_stock(test_url)
    print(f"In stock: {result}")
