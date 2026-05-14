#!/usr/bin/env python3
"""Run Apify Meta Ad Library scraper. Usage: apify-meta-ads.py "BrandName" [--country RU] [--limit 50] [--output path.json]"""
import argparse, json, os, sys, time, urllib.request, urllib.parse

ACTOR = "apify~facebook-ads-scraper"

def api(path, method="GET", body=None, token=""):
    url = f"https://api.apify.com{path}?token={token}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method,
                                  headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())

def main():
    p = argparse.ArgumentParser()
    p.add_argument("brand")
    p.add_argument("--country", default="US")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--output", default=None)
    p.add_argument("--timeout", type=int, default=600)
    args = p.parse_args()

    token = os.environ.get("APIFY_TOKEN")
    if not token:
        sys.exit("APIFY_TOKEN not set (source ~/.claude/.env)")

    # Start run
    input_data = {
        "searchQuery": args.brand,
        "countryCode": args.country,
        "count": args.limit,
        "activeStatus": "all",
    }
    print(f"Starting Apify run for '{args.brand}' country={args.country}...", flush=True)
    start = api(f"/v2/acts/{ACTOR}/runs", method="POST", body=input_data, token=token)
    run_id = start["data"]["id"]
    dataset_id = start["data"]["defaultDatasetId"]
    print(f"  run_id={run_id} dataset={dataset_id}", flush=True)

    # Poll until done
    t0 = time.time()
    while True:
        if time.time() - t0 > args.timeout:
            sys.exit("Timeout waiting for Apify run")
        info = api(f"/v2/actor-runs/{run_id}", token=token)
        status = info["data"]["status"]
        if status in ("SUCCEEDED", "FAILED", "TIMED-OUT", "ABORTED"):
            print(f"  status={status} after {int(time.time()-t0)}s")
            if status != "SUCCEEDED":
                sys.exit(f"Run ended with status {status}")
            break
        print(f"  status={status}, waiting 15s...", flush=True)
        time.sleep(15)

    # Fetch dataset
    items = api(f"/v2/datasets/{dataset_id}/items", token=token)
    print(f"Got {len(items)} ads")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        print(f"Saved to {args.output}")
    else:
        for it in items[:3]:
            print(json.dumps(it, ensure_ascii=False)[:200])

if __name__ == "__main__":
    main()
