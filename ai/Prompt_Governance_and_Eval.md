# Prompt Governance & Eval
- **Style guide**: tone, brand-safe vocabulary, escalation phrases.
- **Policy**: blocked words/patterns aligned with `customer_service.yml`.
- **Eval**:
  - Winograd-style grounding checks.
  - Safety: negate blocked list; check PII redaction.
  - Regression set of 50 real tickets; track accuracy/deflection rate.
- **A/B**: bucket by user hash; significance via sequential tests.
