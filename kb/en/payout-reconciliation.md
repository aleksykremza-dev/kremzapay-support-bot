---
id: KB-083
category: payouts
lang: en
title: Reconciling payouts with orders
---

# Reconciling payouts with orders

Reconciliation means confirming that every payment in a kremzaPay payout matches an order in your own system. The key to doing this reliably is the **sessionId**.

Every payment row in the settlement report carries a unique **sessionId**. When a payment is created, that same sessionId is available on your side, so you can map each settled payment back to the exact order it belongs to.

We recommend a simple daily routine:

1. Open **Reports** and export the settlement data as CSV for the day (or your chosen range).
2. For each row, take the **sessionId** and match it against the order id stored in your system.
3. Confirm the amount and currency agree with what you expected for that order.
4. Set aside any **unmatched rows** — payments with no corresponding order, or orders with no matching payment.
5. Investigate the unmatched rows before contacting support.

Most unmatched rows have a straightforward explanation: a refund applied on a later day, a payment that is still `pending` rather than `completed`, or an order recorded under a different reference. Working through them yourself first usually resolves the discrepancy quickly.

Doing this every day keeps the volume small and makes problems easy to spot, rather than letting differences accumulate over a whole month.

If, after checking the sessionId and the amounts, a row still does not make sense, raise a ticket in the panel or email pomoc@kremzapay.demo (Mon–Fri, 8:00–18:00 CET). Include the sessionId and the payout id so we can trace it immediately.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
