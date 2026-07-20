---
id: KB-092
category: security
lang: en
title: A transaction looks suspicious — what to do
---

# A transaction looks suspicious — what to do

Even when a payment reaches the `completed` status, an order can still look wrong. kremzaPay's anti-fraud runs on the payment side, but you know your products, margins and typical buyers better than any system. Trust that instinct.

Watch for these warning signs:

1. Mismatched buyer data — the name, email, billing details and delivery address do not line up, or the address looks unrelated to the buyer.
2. Unusual amount series — several orders of the same high value in quick succession, or amounts that do not match normal shopping behaviour.
3. Several cards on one delivery address — different cards or buyers repeatedly shipping to the same address.

If something feels off, do not ship while in doubt. Recovering goods after dispatch is far harder than pausing an order.

Follow these steps:

1. Hold the shipment. Do not hand the parcel to the courier yet.
2. Verify the order with the buyer. Contact them using details you trust and confirm they placed it. A genuine customer will usually respond; a fraudulent order often goes silent.
3. Open a support ticket in the Panel and include the `sessionId` of the payment so we can look at it on our side.

Keep the order on hold until you have a clear answer. If you cannot confirm the buyer, treat the order as high risk.

You can find the payment and its `sessionId` under Payments in the Panel. For help, open a ticket or write to pomoc@kremzapay.demo (Mon–Fri 8:00–18:00 CET). Always include the `sessionId` — it lets us find the exact transaction quickly.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
