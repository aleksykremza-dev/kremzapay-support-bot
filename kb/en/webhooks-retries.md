---
id: KB-014
category: integration
lang: en
title: Webhook confirmation and retries
---

# Webhook confirmation and retries

kremzaPay expects your endpoint to confirm every webhook. When it does not, the notification is retried on a schedule.

## What counts as confirmation

A webhook is confirmed when your endpoint replies with HTTP **200** and the body **`OK`**. Any other response — a different status code, a different body, a timeout, or no response — is treated as a failure to confirm.

## Retry schedule

If a notification is not confirmed, kremzaPay retries it:

- Up to **8 times**.
- Within a **24-hour** window from the first attempt.
- At **increasing intervals**, so early retries are close together and later ones are spread further apart.

After 8 unconfirmed attempts within 24 hours, the notification is **dropped** and no further automatic attempts are made.

## Your payment status is still correct

A dropped notification does not change the payment itself. The payment status in the Panel (pending, authorized, completed, failed or expired) always reflects the real outcome, even if your server never confirmed the webhook. Use the Panel as the source of truth when in doubt.

## Resending manually

Every payment has a **resend notification** button. Open the payment in the Panel and use it to trigger the webhook again — useful after you fix an endpoint that was down or returning the wrong response.

If retries keep failing, check that your endpoint returns `200`/`OK` quickly and is reachable over public HTTPS. For help, open a ticket from the Panel or email pomoc@kremzapay.demo.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
