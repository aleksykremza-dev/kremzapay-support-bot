---
id: KB-076
category: integration
lang: en
title: Embedded payment widget
---

# Embedded payment widget

The kremzaPay payment widget is a JavaScript component that embeds method selection directly on your checkout page. The buyer chooses a payment method without leaving your site, which keeps the checkout experience consistent with your own design.

## How it works

1. Your backend creates a transaction through the kremzaPay API and receives the data needed to initialise the widget.
2. Your checkout page loads the widget script and renders the method selection inside a container you place on the page.
3. The buyer picks a method and confirms the payment. For most methods the payment is completed inline, on your page.

The widget handles the presentation and the exchange with kremzaPay. Your backend still registers the transaction server-side and relies on the webhook notification to confirm the final status.

## Fallback redirect

Some payment methods cannot be completed inline because they require the buyer to authenticate on an external page — for example logging in to their bank or passing 3D Secure. For these methods the widget performs a fallback redirect: the buyer is sent to the required page and then returned to your checkout. Design your return page so it can display a clear result once the buyer comes back, and always confirm the outcome from the webhook rather than from the redirect alone.

## Environments

Use the sandbox environment (`api.sandbox.kremzapay.demo`) while integrating, then switch to production (`api.kremzapay.demo`). Each environment has its own keys.

Test both the inline flow and the fallback redirect before going live. If you need assistance, open a ticket in the Panel or write to pomoc@kremzapay.demo (Mon–Fri 8:00–18:00 CET).

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
