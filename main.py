"""
Florida MyFloridaMarketPlace (MFMP) - free, one-off sample puller.

Sends a single request to the same public search endpoint that powers
MyFloridaMarketPlace's own Vendor Bid System search page
(https://vendor.myfloridamarketplace.com/search/bids), asking for currently
OPEN procurement advertisements, and saves a small sample of the raw JSON
response to a local file.

This is a free, local, one-off script: one run, one file, no memory of what
it already showed you. It does not schedule itself, does not track what
changed between runs, does not retry failed requests, and has no
dead-letter handling for records that fail partway through. See README.md
for the honest list of what this does and doesn't do, and for the hosted,
paid Apify actor this repo funnels toward.
"""

import json
import sys

import requests

BASE_URL = "https://vendor.myfloridamarketplace.com"
SEARCH_PATH = "/mfmp/pub/search/bids"

# The portal's search endpoint only answers with JSON when the request
# carries an explicit Accept: application/json header. Without it, the
# server returns its Angular app's index.html shell (HTTP 200, text/html)
# instead of data, which is why the content-type is checked explicitly
# below rather than assumed.
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "florida-tenders-monitor-stub/1.0 (+https://apify.com/stefano_seggio/florida-tenders-monitor)",
}

# Same request body shape the portal's own search page posts. Every key
# must be present or the endpoint answers HTTP 400 - this script asks for
# page 1 of OPEN advertisements with every other filter left empty.
PAYLOAD = {
    "pageSize": 20,
    "type": [],
    "status": ["OPEN"],
    "agency": [],
    "adNumber": "",
    "agencyAdvertisementNumber": "",
    "title": "",
    "publishedDate": "",
    "openDate": "",
    "endDate": "",
    "commodityCodes": [],
    "intendsToParticipate": "",
    "assignee": "",
    "page": 1,
}

MAX_RECORDS = 20
OUTPUT_FILE = "florida_tenders_sample.json"


def fetch_open_advertisements():
    """Fetch page 1 of OPEN advertisements. Returns a list, or None on failure."""
    url = f"{BASE_URL}{SEARCH_PATH}"

    try:
        response = requests.post(url, headers=HEADERS, json=PAYLOAD, timeout=30)
    except requests.exceptions.RequestException as exc:
        # No retry: this is a one-off pull. If the request fails, say so and stop.
        print(f"ERROR: request to {url} failed: {exc}")
        return None

    if response.status_code != 200:
        print(f"ERROR: {url} returned HTTP {response.status_code}: {response.text[:300]}")
        return None

    content_type = response.headers.get("content-type", "")
    if "application/json" not in content_type.lower():
        print(
            f"ERROR: {url} returned content-type '{content_type}' instead of JSON "
            "(this usually means the portal served its Angular app shell rather than API data)."
        )
        return None

    try:
        data = response.json()
    except ValueError as exc:
        print(f"ERROR: could not parse JSON from {url}: {exc}")
        return None

    if not isinstance(data, list):
        print(f"ERROR: expected a JSON array of advertisements from {url}, got {type(data).__name__}")
        return None

    return data


def main():
    advertisements = fetch_open_advertisements()
    if advertisements is None:
        sys.exit(1)

    sample = advertisements[:MAX_RECORDS]

    print(f"Fetched {len(advertisements)} OPEN advertisement(s) from page 1 of the MFMP search endpoint.")
    print(f"Saving a sample of {len(sample)} record(s) to {OUTPUT_FILE}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(sample, f, indent=2, ensure_ascii=False)

    if sample:
        print("\nFirst record in the sample:")
        print(json.dumps(sample[0], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
