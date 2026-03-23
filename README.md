# Pokemon TCG Retail Stock Tracker

A lightweight stock monitor for Pokemon TCG products across major retailers.

It checks product pages using `curl_cffi` browser impersonation, tracks prior stock state in `state.json`, and sends alerts through `ntfy` only on a stock transition from out-of-stock to in-stock.

## Current Progress

### Completed
- Phase 1: Project setup and Python environment
- Phase 2: Notification system via `ntfy.sh`
- Phase 3: Store checkers created for Best Buy, Target, Walmart, GameStop, Barnes & Noble, and CVS
- Phase 4: Main orchestrator (`tracker.py`) with:
  - config loading
  - state loading/saving
  - per-product and per-store check loop
  - false->true notification gating
  - peak-time interval logic
  - continuous run loop with timestamped logs

### Working Right Now
- Target checker: live requests succeed with `impersonate="chrome120"`
- Walmart checker: live requests succeed with `impersonate="chrome120"`
- Barnes & Noble checker: checker runs and parses page text correctly
- Notification sender: confirmed working with `ntfy`
- Tracker orchestration loop: implemented and runnable

### Benched / Not Reliable Yet
- Best Buy checker: currently benched in code due to Akamai connection/internal blocking patterns
- GameStop checker: can return HTTP 403 due to DataDome protection
- CVS checker: logic implemented, but test URL in checker may return 404 depending on product URL validity

## Project Structure

- `tracker.py`: main loop/orchestrator
- `config.json`: products, store IDs/URLs, and polling intervals
- `state.json`: last-known in-stock state per product/store key
- `notifiers/ntfy_notifier.py`: ntfy push notifications
- `checkers/`: one checker module per store
  - `bestbuy.py`
  - `target.py`
  - `walmart.py`
  - `gamestop.py`
  - `barnesnoble.py`
  - `cvs.py`

## How It Works

1. `tracker.py` loads `config.json`.
2. For each product and each configured store, it calls the corresponding checker.
3. Checker returns `True` if stock signal is found in page/API response text, otherwise `False`.
4. Result is compared against last state in `state.json`.
5. Notification is sent only when current is `True` and previous is `False` (or missing).
6. State is saved immediately after each store check.
7. Loop sleeps for peak or normal interval.

## Peak-Time Logic

`is_peak_time()` is active between:
- Thursday 8:00 PM (local time)
- Friday 2:00 PM (local time)

When in peak time, tracker uses `peak_check_interval_minutes`; otherwise it uses `check_interval_minutes`.

## Setup

## 1) Create and activate venv

```bash
python3 -m venv venv
source venv/bin/activate
```

## 2) Install dependencies

```bash
pip install -r requirements.txt
```

## 3) Optional env var for ntfy topic

If unset, notifier defaults to `poke-harshit-test123`.

```bash
export NTFY_TOPIC="your-topic-name"
```

## 4) Configure products

Edit `config.json` and fill each store value appropriately:
- `target`: TCIN
- `walmart`: item ID
- `barnesnoble`: full product URL
- `cvs`: full product URL
- `bestbuy`: SKU (currently benched checker)
- `gamestop`: full product URL

## Run

```bash
python tracker.py
```

You should see timestamped logs for each check and sleep interval.

## Notes and Gaps

- `schedule` is listed in `requirements.txt` but not currently used, because scheduling is implemented with `while True` + `time.sleep()`.
- Some store pages are heavily bot-protected and may intermittently fail despite browser impersonation.
- `state.json` is expected to change during runtime and is gitignored.

## Suggested Next Steps

- Add retry/backoff logic for transient HTTP failures.
- Add per-store cooldown after repeated 403/429 responses.
- Add optional debug mode to save response snippets for failed checks.
- Validate and replace placeholder URLs/IDs in `config.json` before long-running use.
