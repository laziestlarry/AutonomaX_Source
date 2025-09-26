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

---

## AutonomaX Business Unit - AI Powered Business Organization

Supply a superior core intelligence on improvement of business perfection for following goals achievement by selective technologies contribution to associated prompts realization in cooperation. 

## 0. Replace [placeholders] with project factors, through specs determined in means of logic, methods, functions, classifications and parameters definitions.

## 1. Profit Radar: Spot the gaps our competitors miss
Prompt: Analyze my business idea of [concept] for [target audience]. Identify market gaps, high-potential niches, 3 competitors to watch, current trends, customer pain points & pricing insights.

## 2. Offer That Prints Money: Turn ‘meh’ products into must-buys
Prompt: Turn [product/service] into a high-value offer that [target audience] can’t ignore. Include bonuses, pricing psychology & value-boost tactics.

## 3. Instant Brand-in-a-Box: Your name, look, and story; done in minutes
Prompt: Create a complete brand identity for my [business type] targeting [specific demographic]. Suggest brand names, a tagline, color palette, tone, and a short brand story.

## 4. Website That Sells While You Sleep: Pages that close clients, not just sit pretty
Prompt: Design a high-converting website for my [business type] with page layouts & copy ideas for homepage, about, sales page & FAQ. Focus on trust & killing objections.

## 5. 7-Day Hype Machine: rom zero buzz → full-blown launch"
Prompt: Build a 7-day product launch plan for my [business] targeting [audience] on [platforms]. Include pre-launch content, email themes & launch-day CTAs.

## 6. Zero-Ad Sales Plan: Your first customers without spending a cent
Prompt: Step-by-step plan to sell my [product/service] using only my personal network, Instagram & Canva skills — no paid ads.

## 7. Objection Killer: Flip ‘not sure’ into ‘where do I pay?’
Prompt: List the top 5 objections to buying my [product/service] & write persuasive, trust-building responses to each.

## 8. Partnership Power Plays: Borrow audiences bigger than yours
Prompt: Suggest 5 potential partnerships for my [business type] that can drive traffic, boost credibility & reach more customers fast.

## 9. 60-Day Scale Sprint: A roadmap to growth without burning out
Prompt: Create a 60-day growth plan for my [business] focused on growing my email list, launching a mini-course & testing offers. Include milestones, tools & KPIs.

And finally…
## 10. Automation Money Machine: Set it up, let systems earn forever.

