---
id: KB-078
category: integration
lang: en
title: API rate limits
---

# API rate limits

To keep the platform stable for everyone, the kremzaPay API applies a rate limit of 100 requests per minute per merchant. The limit is counted across your account, so it covers all requests made with your keys regardless of which server sends them.

## What happens when you exceed the limit

When you go over 100 requests in a minute, the API responds with HTTP status `429 Too Many Requests`. The response includes a `Retry-After` header telling you how many seconds to wait before sending further requests. Read that header and pause your calls until the window resets, instead of retrying immediately.

## What does not count

- **Batch endpoints** — requests to batch endpoints do not count toward the per-minute limit, so use them when you need to process many items at once.
- **Webhooks** — the notifications kremzaPay sends to your server are not counted against your limit. Webhooks are the recommended way to learn about status changes, and relying on them lets you avoid polling the API repeatedly.

## Staying within the limit

- Use webhooks instead of polling for payment status.
- Use batch endpoints for bulk operations.
- Space out non-urgent requests rather than sending them in bursts.
- Handle `429` responses gracefully by honouring `Retry-After` and backing off.

## Need a higher limit

If your legitimate traffic regularly approaches 100 requests per minute, contact support to request a higher limit. Open a ticket in the Panel or write to pomoc@kremzapay.demo (Mon–Fri 8:00–18:00 CET), and describe your expected request volume.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
