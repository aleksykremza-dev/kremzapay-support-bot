---
id: KB-022
category: security
lang: en
title: 3D Secure 2 explained
---

# 3D Secure 2 explained

3D Secure 2 (3DS2) is a bank-side verification step for card payments. When your customer pays, their card-issuing bank may ask them to confirm the transaction — usually by approving it in their banking app, using biometrics (fingerprint or face), or entering a one-time code. kremzaPay does not perform this check itself; it is handled directly between the customer and their bank.

For payments in the European Economic Area (EEA), 3DS2 is required under Strong Customer Authentication rules. Most card payments processed through kremzaPay will therefore trigger a verification prompt.

## Why it matters

3DS2 reduces fraud by confirming that the person paying is the genuine cardholder. It also shifts chargeback liability for fraudulent transactions: when a payment is successfully authenticated, the responsibility for fraud-related disputes generally moves from you, the merchant, to the card issuer.

## What happens when verification fails

If the customer cannot complete the bank verification — for example, they cancel the prompt, enter the wrong code, or the bank declines — the payment fails. In the kremzaPay Panel this appears as a `failed` payment. In this case the customer is not charged, and no funds are transferred.

## What you should do

1. Ask customers to keep their banking app installed and up to date.
2. If a customer reports a failed payment, suggest they retry and complete the bank confirmation.
3. Check the payment status under Payments in the Panel to confirm whether authentication succeeded.

Verification is controlled by the customer's bank, so you cannot bypass or disable it for EEA card payments.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
