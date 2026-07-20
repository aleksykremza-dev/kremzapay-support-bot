---
id: KB-070
category: integration
lang: en
title: Verifying a transaction
---

# Verifying a transaction

Verification is the final step that closes the payment loop. After kremzaPay sends the webhook notifying you of a payment, you confirm the result back to us. Skipping this step is the most common integration mistake.

**Why it is required**

The webhook tells you a payment status has changed, but your integration must acknowledge that it received and accepted the correct amount and currency. Until you verify, the payment loop is not closed and you should not treat the order as paid.

**The request**

After the webhook arrives, send a `POST` request to `/transaction/verify` with:

- `sessionId` — the identifier of the payment being confirmed.
- `amount` — the amount in grosze, matching the value you registered.
- `currency` — the currency code from the original registration.
- `signature` — the SHA-384 signature of `{sessionId, merchantId, amount, currency, crcKey}`.

**Order of steps**

1. Register the transaction and redirect the buyer.
2. Receive the webhook and verify its signature.
3. Send the verify request with the details above.
4. Only after a successful verify, mark the order as paid and fulfil it.

**Common mistakes**

- Treating the buyer's return to `urlReturn` as confirmation. It is not; only verification confirms payment.
- Verifying with the wrong `amount` or `currency`. These must match the registered transaction exactly.
- Skipping verification entirely, leaving orders in an unconfirmed state.

If verification keeps failing, check the field order and values used to build the signature, then contact support at pomoc@kremzapay.demo.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
