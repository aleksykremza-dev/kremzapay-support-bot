---
id: KB-013
category: integration
lang: en
title: Setting up webhooks
---

# Setting up webhooks

Webhooks let kremzaPay notify your server whenever a payment changes status, so you do not have to poll the API.

## Configure the notification URL

1. Log in to the kremzaPay Panel.
2. Open **Settings**.
3. Go to the **Notifications** tab.
4. Enter your notification URL and save.

Requirements for the URL:

- It must be **public** — reachable from the internet, not a localhost or private address.
- It must use **HTTPS**.

## What kremzaPay sends

On every status change (for example pending → authorized → completed, or a move to failed or expired), kremzaPay sends an HTTP **POST** to your notification URL. The request body contains the payment data for that event.

## How to confirm receipt

Your endpoint must reply with HTTP status **200** and the body **`OK`**. This tells kremzaPay the notification was received.

If you reply with anything else — a different status code, a different body, or nothing — kremzaPay treats the notification as undelivered and will retry.

## Quick checklist

- URL is public and served over HTTPS.
- Endpoint accepts POST requests.
- Endpoint reads the payment data from the request body.
- Endpoint returns `200` with body `OK`.

For retry behavior and manual resends, see the article on webhook confirmation and retries. If notifications are not arriving, open a ticket from the Panel or email pomoc@kremzapay.demo.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
