---
id: KB-008
category: payments
lang: en
title: Card payments and 3D Secure
---

# Card payments and 3D Secure

kremzaPay accepts card payments with **3D Secure 2 (3DS2)**, an authentication step that confirms the cardholder is the person making the purchase. This extra check reduces fraud and unauthorized charges.

## How 3D Secure 2 works

1. The customer enters their card details on the payment page.
2. The card's issuing bank triggers a 3DS2 verification step.
3. The customer confirms the payment, usually by approving it in their bank's mobile app or entering a code sent by the bank.
4. Once the bank verifies the customer, the payment is authorized and then completed.

Most verifications happen in seconds and require a single tap in the banking app.

## Why it is required

Under EEA regulations (Strong Customer Authentication), 3D Secure verification is **required** for most card payments in the European Economic Area. This is a bank and regulatory requirement, not an optional setting.

## When 3D Secure fails

If the customer does not complete or does not pass the 3DS2 step, the result is a **failed** payment:

- The payment status becomes failed.
- The customer was **not** charged.
- The customer can start a new payment and try again, making sure they have their banking app ready to confirm.

## Need help

If your customers report repeated 3D Secure problems, open a ticket from the Panel or email pomoc@kremzapay.demo (Mon–Fri 8:00–18:00 CET).

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
