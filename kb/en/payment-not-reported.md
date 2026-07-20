---
id: KB-009
category: payments
lang: en
title: Payment completed but the shop shows pending
---

# Payment completed but the shop shows pending

Sometimes a payment shows as **completed** in the kremzaPay Panel, but your shop still shows it as pending or unpaid. This almost always means your shop did not receive or confirm the notification (webhook) that kremzaPay sent.

## How notifications work

When a payment changes status, kremzaPay sends a **POST** request to your shop's notification URL. Your shop must reply with **HTTP 200** and the body **OK**. If we do not get that confirmation, we retry up to **8 times within 24 hours** at increasing intervals.

If your shop never confirms, it never updates the order — even though the payment succeeded on our side.

## How to fix it

1. Open the **Payments** section in the Panel and find the transaction.
2. Confirm the status is completed on our side.
3. Go to **Settings** and check your notification URL. Make sure it is correct, reachable, and returns HTTP 200 with the body OK.
4. Open the payment and use the **Resend notification** button to send the webhook again.
5. Confirm the order now updates in your shop.

## Common causes

- Notification URL is wrong, offline, or blocked by a firewall.
- Your endpoint returned an error instead of HTTP 200 / OK.
- Your endpoint took too long to respond.

## Need help

If notifications still do not arrive after checking your settings, open a ticket from the Panel or email pomoc@kremzapay.demo (Mon–Fri 8:00–18:00 CET).

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
