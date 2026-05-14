#!/usr/bin/env python3
"""Exa API search. Usage: exa-search.py "query" [--num N] [--text] [--output path.json]"""
import argparse, json, os, sys, urllib.request

def main():
    p = argparse.ArgumentParser()
    p.add_argument("query")
    p.add_argument("--num", type=int, default=15)
    p.add_argument("--text", action="store_true", help="include full text")
    p.add_argument("--output", default=None)
    args = p.parse_args()

    key = os.environ.get("EXA_API_KEY")
    if not key:
        sys.exit("EXA_API_KEY not set (source ~/.claude/.env)")

    body = {"query": args.query, "numResults": args.num}
    if args.text:
        body["contents"] = {"text": True}

    req = urllib.request.Request(
        "https://api.exa.ai/search",
        data=json.dumps(body).encode(),
        headers={
            "x-api-key": key,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode())

    if args.output:
        with open(args.output, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(data.get('results', []))} results to {args.output}")
    else:
        for r in data.get("results", []):
            print(f"- {r.get('title', '?')}\n  {r.get('url', '')}")
        print(f"\nTotal: {len(data.get('results', []))} results")

if __name__ == "__main__":
    main()
