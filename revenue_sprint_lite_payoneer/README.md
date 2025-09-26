# Revenue Sprint (No-Interaction) — Payoneer

## Replace these placeholders in all files
- `{{PAYONEER_CHECKOUT_URL}}` — your Hosted Payment Page (if Payoneer Checkout is enabled)
- `{{YOUR_PAYONEER_EMAIL}}` — your Payoneer-registered email (for Request a Payment)

## Fulfillment (< 2 hours)
```bash
export CLOUD_RUN_URL="https://autonomax-api-71658389068.us-central1.run.app"
bash ops/quick_fulfill.sh
```
Paste logs + 3 insights into `delivery/template.md` and email the client.

## Go live quickly
**Netlify**
```bash
npm i -g netlify-cli
netlify login
cd landing
netlify init
netlify deploy --prod --dir=.
```

**GitHub Pages**
Push this folder to a branch and enable Pages for the path: `revenue_sprint_lite_payoneer/landing`
