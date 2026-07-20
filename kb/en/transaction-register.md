---
id: KB-069
category: integration
lang: en
title: Registering a transaction
---

# Registering a transaction

Registering a transaction is the first step of every payment. You send the payment details to kremzaPay, receive a token in response, and redirect the buyer to the payment page.

**The request**

Send a `POST` request to `/transaction/register` with the following fields:

- `merchantId` — your merchant identifier from the Panel.
- `sessionId` — a unique identifier for this payment. Generate a new value for every attempt; never reuse one.
- `amount` — the amount in the smallest currency unit (grosze), so 49.90 PLN is sent as `4990`.
- `currency` — the currency code, for example `PLN`.
- `description` — a short description shown to the buyer.
- `urlReturn` — the address the buyer returns to after the payment.
- `signature` — the SHA-384 signature of `{sessionId, merchantId, amount, currency, crcKey}`.

**The response**

A successful response contains a `token`. Store it together with your `sessionId` so you can match the later webhook to the correct order.

**Redirecting the buyer**

Redirect the buyer to the kremzaPay payment page using the returned token. The buyer completes the payment there and is sent back to your `urlReturn`.

**Notes**

- A registered session stays valid for 60 minutes. If the buyer does not pay within that window, the session expires and you must register a new transaction.
- The transaction starts in the `pending` status and moves through `authorized` to `completed` as it progresses.
- The `urlReturn` only brings the buyer back; it is not confirmation of payment. Always wait for the webhook and verify the transaction.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
