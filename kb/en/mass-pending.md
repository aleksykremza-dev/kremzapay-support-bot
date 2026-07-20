---
id: KB-117
category: service
lang: en
title: Many payments stuck in pending
---

# Many payments stuck in pending

If a large number of your payments are suddenly stuck in the **pending** status at the same time, this is almost always a bank-side or payment-method-side incident — not a problem with your integration. When many merchants are affected together, the cause sits upstream, with a bank or a specific payment method, and there is nothing wrong with your own code or configuration.

**What to do**

1. **Check the status page first.** Open status.kremzapay.demo and look at the Payments component. During an upstream incident it will show a degraded or down state, often with a note about the affected method.
2. **Do not resend the payments.** Creating new transactions for the same orders will not speed anything up and may lead to duplicates.
3. **Do not cancel them.** Cancelling stuck payments is unnecessary. Statuses update automatically once the incident is resolved — a pending payment will move on to completed or failed by itself.

**Why waiting is the right move**

During these incidents the transaction has usually already been sent to the bank, and it is the confirmation back to kremzaPay that is delayed. Once the upstream issue clears, the queued confirmations flow through and your payment statuses catch up without any action from you.

**When to open a ticket**

Only open a ticket if individual payments remain in pending well after the incident on the status page is marked as resolved. In that case, report it from the Panel and include the affected sessionIds and timestamps so we can trace them.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
