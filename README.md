# florida-tenders-monitor-stub

A free, one-off Python script that pulls a small sample of Florida state-agency
procurement advertisements from **MyFloridaMarketPlace's Vendor Bid System**
(vendor.myfloridamarketplace.com) - the same public search endpoint the
portal's own search page uses - and saves them to a local JSON file. It runs
once, does exactly one thing (fetch page 1 of currently OPEN advertisements),
and has no memory of previous runs: run it twice and you'll pull the same
current snapshot twice, with no idea what changed in between. It is meant as
a honest, inspectable starting point for anyone who wants to see the real
MFMP data shape before deciding whether they need the scheduled, delta-aware,
production version of this scraper.

## Setup and run

```bash
pip install -r requirements.txt
python main.py
```

This sends one POST request to
`https://vendor.myfloridamarketplace.com/mfmp/pub/search/bids` for page 1 of
`status: ["OPEN"]` advertisements, prints the first record to the console,
and writes up to 20 records to `florida_tenders_sample.json` in the current
directory.

## Example output

`florida_tenders_sample.json` is a JSON array of raw advertisement objects,
exactly as the portal's search endpoint returns them (no reformatting). This
is a real record pulled by running `python main.py` against the live
endpoint:

```json
{
    "agencyAdNumber": "DOT-ITB-27-9011-CA",
    "type": "Agency Decision",
    "title": "GRASS SEEDS",
    "openDate": "2026-09-08T21:00:00.000+00:00",
    "closeDate": "2026-09-11T21:00:00.000+00:00",
    "favorite": false,
    "status": "OPEN",
    "typeId": "1",
    "version": 1,
    "advertisementId": 16900,
    "uniqueName": "AD-16900",
    "publishDate": "2026-09-08T18:45:42.000+00:00",
    "organization": {
        "organizationId": 30000021,
        "entity": "550000",
        "shortName": "FDOT",
        "vbsAgency": true,
        "version": 0,
        "name": "Florida Department of Transportation (FDOT)"
    },
    "agency": "Florida Department of Transportation (FDOT)"
}
```

That's the listing endpoint's raw shape: dates as the portal's own raw
timestamps (no UTC/Florida-time normalization, no `daysUntilClose`), agency
identity duplicated both flat (`agency`) and nested under `organization`,
and no `description`, `commodityCodes`, `documents` or `responseContact` -
those only come back from a separate per-advertisement detail request,
which this stub does not make.

## What this doesn't do

This script deliberately stops at "fetch and save." It does **not**:

- **Schedule itself.** There's no cron, no Apify schedule, no daemon - you
  run `python main.py` and it does one pull, right now.
- **Track deltas between runs.** It doesn't remember which `advertisementId`
  or `version` it saw last time, so it can't tell you what's new, amended
  (`version` rose) or changed status since your last run - every run is a
  blind snapshot.
- **Retry on failure.** A timeout, a dropped connection, or an HTTP 429 from
  the portal just prints an error and exits. No backoff, no re-attempt.
- **Handle dead letters.** If a request fails partway through a larger pull,
  there's no queue of failed records to retry or inspect later - it's just
  gone until you run the script again.

For scheduled runs, delta/change-tracking, and reliability guarantees, see
the production actor: https://apify.com/stefano_seggio/florida-tenders-monitor
