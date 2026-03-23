from curl_cffi import requests

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}


def check_stock(tcin: str) -> bool:
    """Return True if Target's product page contains an IN_STOCK signal."""
    url = f"https://www.target.com/p/-/A-{tcin}"
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            impersonate="chrome120",
            timeout=20,
        )
        print(f"  [Target] TCIN {tcin} — HTTP {response.status_code}")
        if response.status_code != 200:
            print(f"  [Target] Unexpected status, skipping.")
            return False

        html = response.text
        in_stock = '"availability_status":"IN_STOCK"' in html
        print(f"  [Target] IN_STOCK string found: {in_stock}")
        return in_stock
    except Exception as e:
        print(f"  [Target] Error checking TCIN {tcin}: {e}")
        return False


if __name__ == "__main__":
    # 88897904 = Pokemon 151 Elite Trainer Box
    tcin = "88897904"
    result = check_stock(tcin)
    print(f"In stock: {result}")
