---
id: KB-010
category: payments
lang: en
title: Payment session lifetime
---

# Payment session lifetime

Every payment created through kremzaPay has a limited lifetime. This article explains how long a payment session stays open and what happens when it runs out.

## How long a session lasts

A payment session lives for **60 minutes** from the moment it is created. During this window, the customer can choose a method — BLIK, card with 3D Secure, fast bank transfer, Google Pay, or Apple Pay — and complete the payment.

If the customer does not pay within 60 minutes, the session **expires** and the payment status changes to expired.

## What "expired" means

- An expired session **cannot be paid**. The old payment link no longer works.
- The customer was **not** charged. No funds are taken for an expired payment.
- To let the customer pay, you need to **create a new payment**. The customer then goes through checkout again with a fresh session.

## What to tell the customer

If a customer says the payment page no longer works or reports an expired payment, ask them to return to your shop and start the purchase again. This generates a new 60-minute session.

## Checking status in the Panel

You can see whether a payment is expired in the **Payments** section. Expired transactions are clearly marked and never move to completed on their own.

## Need help

If you see sessions expiring more often than expected, open a ticket from the Panel or email pomoc@kremzapay.demo (Mon–Fri 8:00–18:00 CET).

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
