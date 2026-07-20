---
id: KB-071
category: integration
lang: en
title: Fixing signature errors
---

# Fixing signature errors

A signature error means the SHA-384 signature you sent does not match the one kremzaPay calculates on our side. The signature is built from `{sessionId, merchantId, amount, currency, crcKey}`. Almost every error comes from a small difference in how those values are assembled. Work through this checklist.

**1. Exact field order**

Concatenate the fields in this exact order: `sessionId`, `merchantId`, `amount`, `currency`, `crcKey`. A different order produces a different hash, even when all the values are correct.

**2. Amount in grosze, not złoty**

The `amount` must be the smallest currency unit. Send `4990` for 49.90 PLN, not `49.90` and not `49,90`. A decimal point or comma in the amount is a frequent cause of failures.

**3. Correct environment's crc_key**

Use the `crc_key` that belongs to the environment you are calling. The sandbox crc_key will never validate against the production URL and vice versa.

**4. UTF-8 without BOM**

Encode the string as UTF-8 without a byte order mark (BOM). A leading BOM changes the bytes that are hashed and breaks the signature.

**5. No extra whitespace**

Do not add spaces, tabs, newlines, or separators between fields. Concatenate the raw values directly, and trim any trailing whitespace from each value.

**How to debug**

1. Print the exact concatenated string before hashing.
2. Confirm the field order matches the list above.
3. Confirm the amount is an integer in grosze.
4. Confirm the crc_key matches the environment.
5. Recompute the SHA-384 hash and compare.

If the signature still fails after these checks, open a Panel ticket or email pomoc@kremzapay.demo.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
