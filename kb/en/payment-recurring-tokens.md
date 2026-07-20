---
id: KB-058
category: payments
lang: en
title: Recurring payments and card tokens
---

# Recurring payments and card tokens

Recurring payments let you charge a saved card without the buyer completing checkout every time. This is useful for subscriptions, memberships, and any regular billing.

## How the card token is created

The first payment always runs as a normal checkout with 3D Secure authentication. When that payment reaches the **completed** status, kremzaPay saves a card token linked to that card. The token is a reference — it does not expose the full card number.

## Charging the token later

Subsequent charges are merchant-initiated and use the token through the API. No buyer action or checkout session is required.

1. Send a charge request with the card token.
2. Provide the amount in the smallest unit (grosze).
3. kremzaPay processes the charge against the saved card.

Merchant-initiated charges do not open a 60-minute payment session, because the buyer is not present.

## Informing the buyer

Before you save a token, you must inform the buyer of the billing schedule: how often they will be charged, the amount, and how to stop. This is a requirement, not an option.

## Deleting a token

A token can be removed in two ways:

- Delete it through the API when the buyer cancels or the schedule ends.
- It becomes unusable automatically when the underlying card is blocked or expires.

Once a token is deleted, any further charge attempt with it will fail. Completed payments and their tokens remain visible in the **Payments** section. If a charge fails, review the payment status and contact the buyer to update the card.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
