from curl_cffi import requests

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}


def check_stock(item_id: str) -> bool:
    """Return True if Walmart's product page contains an IN_STOCK signal."""
    url = f"https://www.walmart.com/ip/{item_id}"
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            impersonate="chrome120",
            timeout=20,
        )
        print(f"  [Walmart] Item {item_id} — HTTP {response.status_code}")
        if response.status_code != 200:
            print(f"  [Walmart] Unexpected status, skipping.")
            return False

        html = response.text
        in_stock = '"availabilityStatus":"IN_STOCK"' in html
        print(f"  [Walmart] IN_STOCK string found: {in_stock}")
        return in_stock
    except Exception as e:
        print(f"  [Walmart] Error checking item {item_id}: {e}")
        return False


if __name__ == "__main__":
    # 1885068414 = Pokemon 151 Elite Trainer Box
    item_id = "1885068414"
    result = check_stock(item_id)
    print(f"In stock: {result}")
