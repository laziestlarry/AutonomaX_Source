Deploy: Netlify (fast) or GH Pages (CI provided below).
MD

# --- GitHub Actions: Deploy landing (Netlify) + fallback to GH Pages ---
cat > ".github/workflows/deploy-lander.yml" <<'YML'
name: Deploy Lander (Netlify + Pages fallback)
on:
  push:
    branches: [ revenue-sprint-bots ]
  workflow_dispatch:

jobs:
  prepare:
    runs-on: ubuntu-latest
    outputs:
      replaced: ${{ steps.replace.outcome }}
    steps:
      - uses: actions/checkout@v4
      - name: Replace placeholders from secrets
        id: replace
        shell: bash
        run: |
          set -euo pipefail
          PCHK="${{ secrets.PAYONEER_CHECKOUT_URL }}"
          PEML="${{ secrets.YOUR_PAYONEER_EMAIL }}"
          for f in \
            revenue_sprint_lite_payoneer/landing/index.html \
            revenue_sprint_lite_payoneer/landing/_redirects \
            revenue_sprint_lite_payoneer/social/post_and_dm.txt; do
              sed -i "s|{{PAYONEER_CHECKOUT_URL}}|${PCHK:-#}|g" "$f"
              sed -i "s|{{YOUR_PAYONEER_EMAIL}}|${PEML}|g" "$f"
          done
      - name: Upload site artifact
        uses: actions/upload-artifact@v4
        with:
          name: site
          path: revenue_sprint_lite_payoneer/landing

  netlify:
    needs: prepare
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with: { name: site, path: site }
      - name: Netlify Deploy
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
        run: |
          npm -g i netlify-cli
          netlify deploy --prod --dir=site

  pages_fallback:
    if: ${{ always() }}
    needs: prepare
    runs-on: ubuntu-latest
    permissions: { pages: write, id-token: write }
    steps:
      - uses: actions/download-artifact@v4
        with: { name: site, path: site }
      - uses: actions/upload-pages-artifact@v3
        with: { path: site }
      - uses: actions/deploy-pages@v4
YML

# --- Google Apps Script “payment email → run fulfillment” bot (instructions file) ---
mkdir -p automations
cat > automations/payoneer_gmail_bot.md <<'BOT'
# Payoneer Gmail Bot (auto-fulfill on payment email)

1) Go to https://script.google.com → New project.
2) Paste this code:

function onPayoneerPayment_(msg) {
  const CLOUD_RUN_URL = 'https://autonomax-api-71658389068.us-central1.run.app';
  const headers = { 'Content-Type':'application/json' };
  UrlFetchApp.fetch(CLOUD_RUN_URL + '/run/backfill/orders',   {method:'post', headers:headers, muteHttpExceptions:true});
  UrlFetchApp.fetch(CLOUD_RUN_URL + '/run/backfill/products', {method:'post', headers:headers, muteHttpExceptions:true});
}

function checkInbox() {
  const query = 'from:(no-reply@payoneer.com) subject:("Payment received") newer_than:1d';
  const threads = GmailApp.search(query, 0, 10);
  for (const th of threads) {
    const msgs = th.getMessages();
    const last = msgs[msgs.length-1];
    if (!last.isStarred()) {
      onPayoneerPayment_(last);
      last.star();
    }
  }
}

3) Triggers → Add Trigger:
   - Function: checkInbox
   - Event: Time-driven → Every 5 minutes

(If your Cloud Run is private, swap UrlFetchApp calls for an HTTPS endpoint you expose via Cloud Scheduler or add IAP/OIDC handling.)
BOT

# --- Commit & push ---
git checkout -b "$BRANCH"
git add "$KIT" .github/workflows/deploy-lander.yml automations/payoneer_gmail_bot.md
git commit -m "Autobots: Payoneer landing + CI deploy + Gmail auto-fulfill"
git push origin "$BRANCH"

echo "✅ Branch $BRANCH pushed. Next: add repo secrets (see below)."