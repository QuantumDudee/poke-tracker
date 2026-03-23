import json
import os
import time
from datetime import datetime
from pathlib import Path

from notifiers.ntfy_notifier import send_notification
import checkers.bestbuy as bestbuy
import checkers.target as target
import checkers.walmart as walmart
import checkers.gamestop as gamestop
import checkers.barnesnoble as barnesnoble
import checkers.cvs as cvs

BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "config.json"
STATE_FILE = BASE_DIR / "state.json"

# ---------------------------------------------------------------------------
# Store dispatcher: maps store name -> (checker_fn, url_builder)
# For ID-based stores, url_builder constructs a human-readable link for the
# notification. For URL-based stores, the config value IS the URL.
# ---------------------------------------------------------------------------

STORE_DISPATCH = {
    "bestbuy": {
        "fn": bestbuy.check_stock,
        "url": lambda val: f"https://www.bestbuy.com/site/{val}.p",
    },
    "target": {
        "fn": target.check_stock,
        "url": lambda val: f"https://www.target.com/p/-/A-{val}",
    },
    "walmart": {
        "fn": walmart.check_stock,
        "url": lambda val: f"https://www.walmart.com/ip/{val}",
    },
    "gamestop": {
        "fn": gamestop.check_stock,
        "url": lambda val: val,
    },
    "barnesnoble": {
        "fn": barnesnoble.check_stock,
        "url": lambda val: val,
    },
    "cvs": {
        "fn": cvs.check_stock,
        "url": lambda val: val,
    },
}

# ---------------------------------------------------------------------------
# State helpers
# ---------------------------------------------------------------------------

def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# ---------------------------------------------------------------------------
# Config helper
# ---------------------------------------------------------------------------

def load_config() -> dict:
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Peak time helper
# Thursday 8:00 PM → Friday 2:00 PM local time
# ---------------------------------------------------------------------------

def is_peak_time() -> bool:
    now = datetime.now()
    weekday = now.weekday()  # Monday=0 … Sunday=6
    hour = now.hour
    minute = now.minute

    # Thursday (3) at or after 20:00
    if weekday == 3 and (hour > 20 or (hour == 20 and minute >= 0)):
        return True
    # Friday (4) before 14:00
    if weekday == 4 and (hour < 14):
        return True
    return False


# ---------------------------------------------------------------------------
# Core check logic
# ---------------------------------------------------------------------------

def check_all_products(config: dict, state: dict) -> None:
    products = config.get("products", [])
    for product in products:
        name = product["name"]
        stores = product.get("stores", {})

        for store_name, store_value in stores.items():
            dispatch = STORE_DISPATCH.get(store_name)
            if dispatch is None:
                print(f"  [WARN] No checker registered for store '{store_name}', skipping.")
                continue

            state_key = f"{name}_{store_name}"
            previous = state.get(state_key, False)

            print(f"  Checking: {name} @ {store_name.title()} ({store_value})")
            try:
                current = dispatch["fn"](store_value)
            except Exception as e:
                print(f"  [ERROR] {store_name} checker raised an exception: {e}")
                current = False

            # Only notify on False → True transition
            if current and not previous:
                product_url = dispatch["url"](store_value)
                print(f"  *** RESTOCK DETECTED: {name} @ {store_name.title()} ***")
                send_notification(
                    title=f"RESTOCK: {name}",
                    message=f"{name} is IN STOCK at {store_name.title()}!",
                    url=product_url,
                )
            elif current and previous:
                print(f"  [INFO] Still in stock (no new alert).")
            else:
                print(f"  [INFO] Out of stock.")

            state[state_key] = current
            save_state(state)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    print(f"[{ts()}] Poke Tracker started.")
    config = load_config()
    normal_interval = config.get("check_interval_minutes", 3) * 60
    peak_interval = config.get("peak_check_interval_minutes", 1) * 60

    while True:
        state = load_state()
        print(f"\n[{ts()}] --- Running stock checks ---")
        check_all_products(config, state)

        peak = is_peak_time()
        sleep_seconds = peak_interval if peak else normal_interval
        interval_label = f"{sleep_seconds // 60}m (peak)" if peak else f"{sleep_seconds // 60}m (normal)"
        print(f"[{ts()}] --- Check complete. Sleeping {interval_label} ---")
        time.sleep(sleep_seconds)
