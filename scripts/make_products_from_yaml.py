#!/usr/bin/env python3
"""Convert a YAML product spec into Shopify-ready JSON."""
import argparse
import json
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("pip install pyyaml to use this tool") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert YAML catalog to Shopify JSON")
    parser.add_argument("source", type=Path, help="YAML file with products list")
    parser.add_argument("--out", type=Path, default=Path("shopify_products.json"))
    args = parser.parse_args()

    data = yaml.safe_load(args.source.read_text())
    products = data.get("products") if isinstance(data, dict) else data
    payload = {"products": products or [], "dry_run": True}
    args.out.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
