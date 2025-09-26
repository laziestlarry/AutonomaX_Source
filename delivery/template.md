# Delivery — AI Store Ops Quickstart

**Client:** {{CLIENT_NAME}}  
**Store:** {{STORE_URL}}  
**Delivery time:** within 2 hours (no meeting)

## 1) Health Check
- Orders endpoint: ✅ / ❌ (notes)
- Products endpoint: ✅ / ❌ (notes)
- Nightly schedules: Enabled / Paused (TZ: {{TIMEZONE}})

## 2) Three Insights
1. **Top 5% SKUs** drive {{PCT}}% revenue → stock & promote (IDs: {{SKU_LIST}})
2. **Pricing nudge**: +3–5% on {{N_SKUS}} top SKUs (7-day check on AOV)
3. **Automation**: Enable nightly sync + anomaly alert

## 3) Next 7 Days
- [ ] Toggle nightly job(s) (02:00/03:00 {{TIMEZONE}})
- [ ] Price test (owner: {{OWNER}})
- [ ] 7-day KPI recap

## 4) Evidence


POST /run/backfill/orders → {"ok": true}
POST /run/backfill/products → {"ok": true}


— Thank you!
