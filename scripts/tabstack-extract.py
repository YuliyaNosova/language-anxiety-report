#!/usr/bin/env python3
"""Compatibility shim. TabStack was replaced by playwright-extract.js.
This wrapper exists so agents that call `tabstack-extract.py` keep working.
"""
import argparse, subprocess, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
PW = os.path.join(HERE, "playwright-extract.js")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("--format", default="markdown", choices=["markdown", "json"])
    p.add_argument("--output", required=True)
    args = p.parse_args()

    flag = "--markdown" if args.format == "markdown" else "--scrape"
    # Run from project root so node_modules resolves
    proj_root = os.path.dirname(HERE)
    cmd = ["node", PW, args.url, flag, "--output", args.output]
    r = subprocess.run(cmd, cwd=proj_root)
    sys.exit(r.returncode)

if __name__ == "__main__":
    main()
