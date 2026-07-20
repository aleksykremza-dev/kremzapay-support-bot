---
id: KB-072
category: integration
lang: en
title: Verifying the webhook signature
---

# Verifying the webhook signature

Every webhook kremzaPay sends carries a signature so you can confirm the notification really came from us and was not tampered with in transit. Always verify the signature before you trust or act on the data.

**How the signature works**

The webhook is delivered as a `POST` request. Its signature is the SHA-384 hash of the payload combined with your `crc_key`. Because only you and kremzaPay know the crc_key, a matching signature proves the payload is authentic and unchanged.

**Verification steps**

1. Read the raw payload exactly as received, without reformatting or re-serialising it.
2. Compute the SHA-384 hash of the payload using your environment's `crc_key`.
3. Compare your computed value with the signature sent in the webhook.
4. If they match, process the notification. If they do not, reject it.

**Rejecting invalid webhooks**

If the signature does not match, do not process the data. Reject the request silently by replying with a non-200 response. kremzaPay treats any non-200 reply as a failed delivery and retries automatically, up to 8 times over 24 hours. A valid webhook should be answered with HTTP 200 and the body `OK`.

**Good practice**

- Verify before parsing business logic, so malformed or forged payloads never reach your order handling.
- Use the crc_key from the same environment that sent the webhook.
- If a legitimate webhook was missed, you can trigger a manual resend from the Panel.

If verification behaves unexpectedly, open a Panel ticket or email pomoc@kremzapay.demo.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
