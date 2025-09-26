# agents.md — CLI-ready playbook (no meetings)

This file lets you delegate tasks to simple “agents” (bots or you via CLI). Copy/paste commands as-is.

---

## Agent 1 — Lander Publisher
**Goal:** Put a no-interaction Payoneer page live fast.

**If using Netlify**
```bash
npm i -g netlify-cli
netlify login
cd revenue_sprint_lite_payoneer/landing
# Replace placeholders in index.html first:
#  - {{PAYONEER_CHECKOUT_URL}} (or keep '#')
#  - {{YOUR_PAYONEER_EMAIL}}
netlify init
netlify deploy --prod --dir=.
```

**If using GitHub Pages**
```bash
git checkout -b revenue-sprint-lite
git add revenue_sprint_lite_payoneer
git commit -m "Revenue sprint (Payoneer, no-interaction)"
git push origin revenue-sprint-lite
# Enable Pages for this branch/path: revenue_sprint_lite_payoneer/landing
```

---

## Agent 2 — Payment → Fulfillment
**Goal:** After payment hits, trigger your Cloud Run backfills and capture a log.

```bash
export CLOUD_RUN_URL="https://autonomax-api-71658389068.us-central1.run.app"
bash revenue_sprint_lite_payoneer/ops/quick_fulfill.sh
# Result file saved under revenue_sprint_lite_payoneer/delivery/output_*.log
# Paste into revenue_sprint_lite_payoneer/delivery/template.md and email the client.
```

**Private Cloud Run?** Use your impersonation token as header (already configured in your env), or keep service public and rely on Scheduler OIDC only.

---

## Agent 3 — Social Promo
**Goal:** Post once, DM 10 targets.
- Use `revenue_sprint_lite_payoneer/social/post_and_dm.txt`
- Replace placeholders and post/DM.

---

## Agent 4 — Cost Guard (Cloud)
**Goal:** Avoid runaway costs.

- Keep `max-instances=2` on `autonomax-api`.
- Pause Scheduler jobs when not in use:
```bash
REGION=us-central1
gcloud scheduler jobs pause orders-nightly-backfill   --location="$REGION"
gcloud scheduler jobs pause products-nightly-backfill --location="$REGION"
# Resume:
gcloud scheduler jobs resume orders-nightly-backfill   --location="$REGION"
gcloud scheduler jobs resume products-nightly-backfill --location="$REGION"
```

---

## FAQ
- **No Payoneer Checkout yet?** Leave `{{PAYONEER_CHECKOUT_URL}}` as `#`. Buyers click “Request Payoneer Invoice” → you send Payoneer “Request a Payment”.
- **Where do I edit the page?** `revenue_sprint_lite_payoneer/landing/index.html`.
- **What do I send the client?** Use `delivery/template.md` + the `output_*.log` evidence.
