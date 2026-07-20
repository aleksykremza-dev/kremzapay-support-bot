---
id: KB-016
category: account
lang: en
title: Sandbox vs production
---

# Sandbox vs production

kremzaPay gives you two separate environments: sandbox for testing and production for real transactions. Understanding the difference keeps test traffic out of your live account.

## Sandbox

Sandbox is a test environment. It behaves like production but processes **no real money**. Instead of real banks and BLIK, it uses test simulators, so you can drive a payment through every status — pending, authorized, completed, failed and expired — without moving funds.

Sandbox has:

- Its own set of keys (merchant_id, api_key, crc_key).
- Its own panel, separate from production.

Because keys and panels are separate, a payment you create in sandbox never appears in production and vice versa.

## Production

Production is the live environment. Requests here use your production keys and result in real charges. Reports, Payments, Refunds and Payouts in the production panel reflect real customer activity.

## Go-live checklist

Before you switch traffic to production, confirm:

1. **Production keys in place** — your code uses the production merchant_id, api_key and crc_key, not the sandbox set.
2. **Signature verified** — the SHA-384 signature validates against your production crc_key.
3. **Webhook URL reachable** — your public HTTPS notification URL replies `200`/`OK` and is set in the production panel.
4. **One real low-value payment tested** — run a single small real payment end to end and confirm it reaches completed status and that the webhook fires.

If anything in the checklist fails, stay on sandbox until it is fixed. For help, open a ticket from the Panel or email pomoc@kremzapay.demo (Mon–Fri 8:00–18:00 CET).

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
