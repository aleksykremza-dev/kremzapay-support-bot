---
id: KB-075
category: integration
lang: en
title: Mobile SDKs (iOS and Android)
---

# Mobile SDKs (iOS and Android)

The kremzaPay mobile SDKs let you accept payments inside your native iOS and Android apps. The SDK presents a native payment sheet, so buyers stay in your app instead of being sent to an external browser.

## What the SDK handles

- Displaying the payment sheet and the hosted payment page inside the app.
- Running 3D Secure (3DS) authentication when the card issuer requires it.
- Returning the payment result to your app so you can update the interface.

The SDK covers the customer-facing part of the flow. It does not replace your backend.

## What your backend still does

The transaction must always be registered server-side. Your backend calls the kremzaPay API to create the transaction, receives the payment identifier and passes only the data the app needs to open the payment sheet. Your server also receives the webhook notification that confirms the final payment status, and that notification remains the source of truth for updating an order.

## Security

Never embed the `crc_key` in the mobile app. Anything shipped inside an app can be extracted, and the `crc_key` is used to sign requests with SHA-384. Keep it on your server only, and perform all signing there. The app should work with short-lived data returned by your backend, not with your secret keys.

## Environments

Use the sandbox environment (`api.sandbox.kremzapay.demo`) during development and testing, then switch to production (`api.kremzapay.demo`) for release. Each environment has its own keys.

Test the full flow, including 3DS and cancelled payments, before publishing your app. For help, open a ticket in the Panel or write to pomoc@kremzapay.demo (Mon–Fri 8:00–18:00 CET).

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
