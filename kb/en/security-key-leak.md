---
id: KB-096
category: security
lang: en
title: API key leak — action plan
---

# API key leak — action plan

If an API key has been exposed — committed to a public repository, pasted into a chat, or leaked in any other way — act immediately. A leaked key can be used to call the API on your behalf until it is revoked.

## 1. Regenerate the keys

1. Open **Settings → API keys**.
2. Select **Regenerate**.

The old key dies instantly. Any request still using it starts failing right away, which stops the attacker but also stops your own integration until the next step is done.

## 2. Update the new key in your integration

Copy the newly generated key and replace the old value everywhere your integration stores it — environment variables, secrets manager, or configuration. Deploy the change so live traffic uses the new key.

## 3. Review recent transactions

Open **Payments** and go through recent activity for anything unexpected: payments you do not recognise, unusual amounts, or refunds you did not initiate. Note anything suspicious.

## 4. Report to support

Raise a ticket in the Panel, or email pomoc@kremzapay.demo (Mon–Fri, 8:00–18:00 CET). Include when the key may have leaked and any anomalies you found, so support can help you assess the impact.

## If the crc_key also leaked

The `crc_key` verifies webhook signatures. If it was exposed as well, rotate it so incoming webhook notifications are validated against the new secret, then update your webhook verification logic to use the rotated value.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
