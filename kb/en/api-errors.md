---
id: KB-015
category: integration
lang: en
title: Common API error codes
---

# Common API error codes

When a request cannot be processed, the kremzaPay API returns an error code. The most common codes and how to resolve them are listed below.

| Error code | Meaning | How to fix |
|---|---|---|
| `err-invalid-signature` | The request signature does not match. | Check the crc_key and the field order used to build the SHA-384 signature. Confirm the amount is in grosze/cents. |
| `err-session-exists` | A payment with this `sessionId` was already registered. | Use a unique `sessionId` for every new payment. Do not reuse an identifier. |
| `err-amount-mismatch` | The amount sent for verification differs from the amount the session was registered with. | Send the same amount you registered, in the smallest currency unit. |
| `err-session-expired` | The 60-minute payment session has passed. | Register a new session and start the payment again. |
| `err-unauthorized` | The api_key is wrong, or it belongs to a different environment. | Check the api_key and confirm you are using the key for the correct environment (sandbox or production). |

## Reading these errors

- **Signature and amount errors** almost always come from a mismatch between what you send and what kremzaPay computes. Re-check the field order and that amounts are in the smallest unit.
- **Session errors** relate to the lifecycle of a payment: a `sessionId` must be unique, and a session is valid for 60 minutes before it expires.
- **Authorization errors** usually mean a sandbox key reached production or the reverse.

If an error persists after these checks, open a ticket from the Panel or email pomoc@kremzapay.demo (Mon–Fri 8:00–18:00 CET) with the sessionId and the error code.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
