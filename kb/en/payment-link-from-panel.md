---
id: KB-055
category: payments
lang: en
title: Creating a payment link from the Panel
---

# Creating a payment link from the Panel

A payment link lets you collect a payment without integrating anything on a website. You create the link in the Panel and send it to your customer, who opens it and pays on a standard kremzaPay payment page.

## How to create a link

1. Go to **Payments → Create payment link**.
2. Enter the **amount**.
3. Choose the **currency** for the payment.
4. Add a short **description** so the buyer knows what they are paying for.
5. Confirm to generate the link.

## Sharing the link

Once the link is created, you can copy it and share it however you like, for example by email or messenger. There is no special channel; any way the customer can open a web address will work.

## Validity and behavior

- Each payment link is valid for **72 hours** from creation.
- A link opened after it expires can no longer be paid.
- Every link is a normal payment: it receives its own **sessionId** and follows the usual statuses (pending, authorized, completed, failed, expired).

Because a payment link is a regular payment, you can track it in **Payments** and handle it later in **Refunds** just like any other transaction.

If a customer reports a problem opening a link, first check whether the 72-hour validity has passed, then create a new link if needed. For further help, open a Panel ticket or write to pomoc@kremzapay.demo, Monday to Friday, 8:00–18:00 CET.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
