---
id: KB-097
category: security
lang: en
title: How payers are verified
---

# How payers are verified

Every payment made through kremzaPay is verified before the money moves. Most of that verification happens on the buyer's bank side, and kremzaPay adds its own checks on top. As a merchant, you never see the buyer's banking credentials.

## Bank-side verification

The method of confirmation depends on how the buyer chooses to pay:

- **BLIK** — the buyer confirms the payment in their banking app, typically with a code and an in-app approval.
- **Cards** — card payments go through 3DS2 authentication, so the buyer confirms with their bank using the method the bank requires.
- **Fast transfers** — the buyer logs in to their own bank to authorise the transfer directly.

In each case the buyer authenticates with their bank, not with you. Passwords, card numbers, and one-time codes stay between the buyer and their bank.

## Risk scoring on top

Once the bank confirms the payer, kremzaPay applies its own risk scoring. This layer looks at signals around the transaction to help catch fraudulent or anomalous activity that passes bank authentication but still looks suspicious. It works quietly in the background and does not require any action from you.

## What merchants can and cannot see

You receive the information needed to fulfil the order and reconcile the payment. You do not receive the buyer's banking credentials, full card numbers, or authentication codes. This keeps sensitive buyer data out of your systems while still giving you what you need to run your business.

If a payment result looks wrong, raise a ticket in the Panel or email pomoc@kremzapay.demo.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
