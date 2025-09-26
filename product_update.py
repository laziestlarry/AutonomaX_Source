#!/usr/bin/env python3
import json, os, subprocess, argparse, pathlib, sys

def load_manifest(root: pathlib.Path):
    p = root / "_autonomax" / "manifest.json"
    if not p.exists():
        print("product_update: manifest.json missing. Run bootstrap first.", file=sys.stderr)
        sys.exit(0)
    return json.loads(p.read_text())

def pick_entry(manifest, needles):
    for e in manifest.get("entries", []):
        fn = (e.get("filename") or "").lower()
        for n in needles:
            if n in fn:
                cp = e.get("chosen_path")
                if cp and os.path.exists(cp):
                    return cp
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", required=True)
    args = ap.parse_args()
    root = pathlib.Path(args.project_root)

    print("▶ Product Update Phase")
    manifest = load_manifest(root)

    shopify_sync = pick_entry(manifest, ["shopify_sync.py"])
    products_csv = pick_entry(manifest, ["shopify/products.csv"])
    make_products = pick_entry(manifest, ["scripts/make_products_from_yaml.py"])

    if shopify_sync and products_csv:
        token = os.environ.get("SHOPIFY_ADMIN_TOKEN")
        domain = os.environ.get("SHOP_DOMAIN") or os.environ.get("SHOPIFY_SHOP_DOMAIN")
        print(f"• sync: {shopify_sync}")
        print(f"• csv:  {products_csv}")
        if token and domain:
            print("• Env OK → running sync (this may take a while)")
            try:
                subprocess.run(["python", shopify_sync, "--csv", products_csv, "--apply"], check=True)
            except Exception as e:
                print(f"(non-fatal) sync failed: {e}")
        else:
            print("• Missing SHOPIFY_ADMIN_TOKEN or SHOP_DOMAIN")
            print(f"  → To run manually: python {shopify_sync} --csv {products_csv} --apply")
    elif make_products:
        print(f"• Found product builder: {make_products}")
        try:
            subprocess.run(["python", make_products], check=True)
        except Exception as e:
            print(f"(non-fatal) builder failed: {e}")
    else:
        print("• No product update script found. Skipping.")

if __name__ == "__main__":
    main()
