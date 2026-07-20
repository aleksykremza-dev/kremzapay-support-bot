---
id: KB-057
category: payments
lang: en
title: Minimum and maximum payment amount
---

# Minimum and maximum payment amount

Every kremzaPay transaction must fall within an allowed amount range. This range protects both you and your buyers from accidental zero-value or oversized payments.

## Default range

By default, a single transaction can be between **1 PLN and 50 000 PLN**. A payment below the minimum or above the maximum is rejected before it starts, and the buyer is asked to use a valid amount.

For shops in another currency, the equivalent range applies based on the shop currency configured for the payment.

## Raising the limits

If your business regularly needs larger transactions, higher limits are available **per agreement**. To request an increase, open a Panel ticket or write to pomoc@kremzapay.demo, Monday to Friday, 8:00–18:00 CET. Describe your typical transaction size so the limit can be set appropriately.

## Amounts in the API

When you send an amount through the API, it is expressed in the **smallest currency unit** rather than in whole units. For example:

- 1 PLN is sent as **100** (grosze).
- 25.50 EUR is sent as **2550** (cents).

Always multiply the whole-currency amount by 100 before sending it, and divide values received back from the API by 100 when displaying them. Using whole units by mistake is a common cause of payments that are 100 times too large or too small.

If a payment is rejected for being outside the range, check both the amount and the currency unit before retrying.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
