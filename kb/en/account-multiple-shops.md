---
id: KB-050
category: account
lang: en
title: Running multiple shops
---

# Running multiple shops

If you operate more than one shop, you do not need a separate kremzaPay account for each. A single account can hold several shops, each kept cleanly apart.

## How multiple shops work

Every shop you add gets its own **merchant_id** and its own set of keys. This keeps each shop's integration independent, so a change to one shop does not affect the others. It also means:

- **Separate reports** — each shop has its own transaction history in Reports, so you can see how each one is performing on its own.
- **Separate payouts** — funds are settled per shop, so the money from each shop is paid out and reconciled independently.

This separation makes it straightforward to run distinct brands, storefronts, or business lines under one login.

## Adding a shop

1. Sign in to your Panel.
2. Open **Settings → Shops**.
3. Add a new shop and confirm its details.
4. Note the new **merchant_id** and generate the keys for that shop.

Use the new shop's own merchant_id and keys in that shop's integration. Remember that sandbox and production keys are separate, so configure each environment with the correct keys for the right shop.

## Keeping shops organised

Give each shop a clear name so its reports and payouts are easy to tell apart. If you need help setting up an additional shop, contact us through a Panel ticket or at pomoc@kremzapay.demo, Monday to Friday, 8:00–18:00 CET.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
