from curl_cffi import requests

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}


def check_stock(url: str) -> bool:
    """Return True if the GameStop product page contains an Add to Cart button."""
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            impersonate="chrome120",
            timeout=20,
        )
        print(f"  [GameStop] {url} — HTTP {response.status_code}")
        if response.status_code != 200:
            print(f"  [GameStop] Unexpected status, skipping.")
            return False

        in_stock = ">Add to Cart<" in response.text
        print(f"  [GameStop] Add to Cart found: {in_stock}")
        return in_stock
    except Exception as e:
        print(f"  [GameStop] Error checking {url}: {e}")
        return False


if __name__ == "__main__":
    test_url = "https://www.gamestop.com/trading-cards/pokemon/products/pokemon-scarlet-violet-151-elite-trainer-box/309693.html"
    result = check_stock(test_url)
    print(f"In stock: {result}")
