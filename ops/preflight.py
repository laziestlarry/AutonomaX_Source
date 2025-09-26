import os, sys, json

REQUIRED = {
    "base": ["ENV"],
    "api_key": ["API_KEY"],
}

def check_env():
    issues = []
    env = os.getenv("ENV","dev")
    # Always check base
    for k in REQUIRED["base"]:
        if not os.getenv(k): issues.append(f"missing {k}")
    # API key recommended for prod
    if env != "dev" and not os.getenv("API_KEY"):
        issues.append("missing API_KEY in non-dev env")
    # Pub/Sub/BQ if enabled
    if os.getenv("PUBSUB_ENABLED","false").lower()=="true" and not os.getenv("GCP_PROJECT_ID"):
        issues.append("PUBSUB_ENABLED=true but GCP_PROJECT_ID missing")
    if os.getenv("USE_OPENAI","false").lower()=="true" and not os.getenv("OPENAI_API_KEY"):
        issues.append("USE_OPENAI=true but OPENAI_API_KEY missing")
    # Webhook hardening
    if env != "dev" and not (os.getenv("SHOPIFY_WEBHOOK_SECRET") or os.getenv("SHOPIFY_API_SECRET")):
        issues.append("non-dev env missing SHOPIFY_WEBHOOK_SECRET/API_SECRET")
    return issues

def main():
    issues = check_env()
    ok = (len(issues) == 0)
    print(json.dumps({"ok": ok, "issues": issues}, indent=2))
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
