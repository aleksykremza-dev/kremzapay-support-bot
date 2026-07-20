---
id: KB-059
category: payments
lang: en
title: Pre-authorization and capture
---

# Pre-authorization and capture

Pre-authorization lets you block funds on a buyer's card without taking them immediately. You capture the money later, once you are ready to fulfil the order. This is common for bookings, rentals, and orders where the final amount is confirmed after checkout.

## Authorized means blocked, not taken

When a payment reaches the **authorized** status, the funds are reserved on the card but have not left the buyer's account. No money is settled to you until you capture it.

## Capturing within 7 days

You must capture an authorized payment within 7 days. If you do not, the hold is released automatically and the funds return to the buyer. After that, you would need a new payment.

To capture:

1. Open the payment in the **Payments** section.
2. Confirm the capture, or send a capture request through the API.
3. The payment moves to **completed** once captured.

## Partial capture

You can capture less than the authorized amount — for example, if part of an order is unavailable. Partial capture is allowed **once** per payment. When you capture a partial amount, the remaining balance is released back to the buyer automatically; you cannot capture it afterwards.

If the buyer needs the released amount charged again, create a new payment. If a capture does not go through, check the payment status and the 7-day window before retrying, and contact support through the Panel ticket system or pomoc@kremzapay.demo if the status looks wrong.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
