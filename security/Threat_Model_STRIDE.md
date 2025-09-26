# Threat Model (STRIDE)
- **Spoofing**: Forged Shopify webhook → mitigated via HMAC.
- **Tampering**: Pub/Sub message integrity → use signed attributes + CMEK on topics.
- **Repudiation**: OTEL trace IDs + audit logs on mutating endpoints.
- **Information Disclosure**: Mask PII, field-level encryption in BQ if required.
- **Denial of Service**: Autoscale min/max instances, rate-limits, circuit breakers.
- **Elevation of Privilege**: IAM scoped roles, no default editor roles.
