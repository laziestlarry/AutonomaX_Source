#!/usr/bin/env python3
"""Sync catalog products to Shopify via the AutonomaX API."""
import argparse
import json
import os
import subprocess
import tempfile
import requests


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync catalog to Shopify")
    parser.add_argument("--limit", type=int, default=20, help="Number of products to send")
    parser.add_argument("--dry-run", action="store_true", help="Do not create products")
    parser.add_argument("--api", default=os.getenv("AUTONOMAX_API_URL", "http://localhost:8080"))
    args = parser.parse_args()

    with tempfile.NamedTemporaryFile("w+", suffix=".json") as tmp:
        subprocess.run(
            [
                "python3",
                "tools/catalog_to_shopify_json.py",
                "--limit",
                str(args.limit),
                "--out",
                tmp.name,
            ],
            check=True,
        )
        payload = json.load(tmp)
    payload["dry_run"] = args.dry_run

    endpoint = f"{args.api.rstrip('/')}/ecom/shopify/import"
    resp = requests.post(endpoint, json=payload, timeout=60)
    resp.raise_for_status()
    print(json.dumps(resp.json(), indent=2))


if __name__ == "__main__":
    main()
