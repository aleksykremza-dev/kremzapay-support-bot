---
id: KB-115
category: service
lang: en
title: Service status page
---

# Service status page

The status page at **status.kremzapay.demo** is the fastest way to check whether kremzaPay is working correctly. It shows the live state of each component of the platform, so you can tell in seconds whether an issue is on our side or in your own integration.

The page reports the current status of these components separately:

- **Payments** — processing of card and transfer transactions
- **Panel** — the merchant panel interface (Payments, Refunds, Payouts, Reports, Settings)
- **API** — programmatic requests to kremzaPay
- **Webhooks** — delivery of payment notifications to your server

Below the component list you will find:

- **Incident history** — past disruptions with start time, resolution time and a short description of what happened
- **Planned maintenance** — upcoming maintenance windows announced in advance

To stay informed automatically, subscribe to email updates directly on the status page. You will then receive a message when an incident is opened, updated or resolved, and when maintenance is scheduled.

When something looks wrong — payments not completing, the panel not loading, webhooks not arriving — check the status page first, before you change your integration or open a ticket. If a component is marked as degraded or down, the issue is already known and our team is working on it; you do not need to report it again. If every component shows green and the problem continues, then it is worth opening a ticket from the Panel.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
