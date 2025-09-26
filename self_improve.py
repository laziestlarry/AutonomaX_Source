#!/usr/bin/env python3
import argparse, pathlib

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-root", required=True)
    args = ap.parse_args()
    root = pathlib.Path(args.project_root)

    out = root / "_autonomax"
    out.mkdir(parents=True, exist_ok=True)
    rpt = out / "self_improve_todo.md"

    checks = []
    checks.append(("Python venv", (root / ".venv").exists(), "create with: python3 -m venv .venv"))
    checks.append(("requirements.txt", (root / "requirements.txt").exists(), "generate or maintain"))
    checks.append(("package.json", (root / "package.json").exists(), "npm init -y or maintain"))
    checks.append((".git", (root / ".git").exists(), "git init && git add -A && git commit -m 'init'"))

    lines = ["# Self-Improve TODOs", ""]
    for name, ok, hint in checks:
        badge = "✅" if ok else "⚠️"
        lines.append(f"- {badge} **{name}** {'OK' if ok else hint}")

    lines += [
        "",
        "## Suggested Next Actions",
        "1) Copy `.env.example` to `.env` and fill SHOP_DOMAIN, SHOPIFY_ADMIN_TOKEN.",
        "2) If Node: `npm install` then `npm run build`.",
        "3) If Python: `pip install -r requirements.txt`.",
        "4) Ensure CI at `.github/workflows/deploy.yml` can run without secrets leakage.",
        "5) Run `make ignite-all` to repeat all phases after fixes."
    ]

    rpt.write_text("\n".join(lines), encoding="utf-8")
    print(f"• Wrote {rpt}")

if __name__ == "__main__":
    main()
