---
id: KB-012
category: integration
lang: en
title: Request signature (SHA-384)
---

# Request signature (SHA-384)

kremzaPay verifies each request with a signature. The signature is a SHA-384 hash built from a fixed set of fields, in a fixed order.

## How to build it

Concatenate the following fields and hash the result with SHA-384:

1. `sessionId`
2. `merchantId`
3. `amount`
4. `currency`
5. `crcKey`

Send the resulting hash as the request signature. The `crcKey` is part of the hashed input only — it is never sent as a separate field.

## Field notes

- **amount** is expressed in the smallest currency unit (grosze for PLN, cents for EUR/USD). For example, 49.90 PLN is `4990`.
- **currency** uses the standard code: PLN, EUR, USD, GBP or CZK.
- The field order above is required. Changing it produces a different hash and the request is rejected.

## Most common mistakes

- **Wrong field order** — the fields must be combined exactly as listed above.
- **Amount in złoty instead of grosze** — sending `49.90` instead of `4990` gives a signature that does not match what kremzaPay computes.
- **Sandbox crc_key used in production** — each environment has its own crc_key. A sandbox key will never verify against production.

If the signature does not match, kremzaPay returns an invalid-signature error. Re-check the field order, the amount unit, and the environment of your crc_key. For help, open a ticket from the Panel or email pomoc@kremzapay.demo.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
