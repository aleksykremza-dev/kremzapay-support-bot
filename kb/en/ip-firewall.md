---
id: KB-079
category: integration
lang: en
title: IP addresses and firewall rules
---

# IP addresses and firewall rules

If your server filters incoming traffic with a firewall, you need to allow kremzaPay webhook notifications to reach your endpoint. This page explains which addresses to allow and how API traffic works in the other direction.

## Webhook source addresses

Webhook notifications originate from a defined range of IP addresses. The current range is listed in Panel → Settings → Notifications. If your server restricts inbound connections, add that range to your allow-list so notifications are not blocked before they reach your webhook endpoint.

Check the listed range periodically. If it changes, update your firewall rules accordingly, otherwise notifications may start failing. Remember that kremzaPay retries an undelivered webhook up to 8 times over 24 hours, and your endpoint should respond with HTTP `200` and the body `OK` once it has received and accepted a notification.

## Outgoing API traffic

Requests you send to the kremzaPay API go to public HTTPS endpoints, so no special inbound firewall rule is needed for them. The endpoints require TLS 1.2 or higher — make sure your HTTP client and TLS libraries are up to date so the connection is not rejected.

The API hosts are:

- Sandbox: `api.sandbox.kremzapay.demo`
- Production: `api.kremzapay.demo`

## Checklist

1. Allow-list the webhook IP range from Panel → Settings → Notifications.
2. Confirm your webhook endpoint answers with `200 OK`.
3. Ensure outgoing connections use TLS 1.2 or higher.

If notifications still do not arrive after allow-listing the range, open a ticket in the Panel or write to pomoc@kremzapay.demo (Mon–Fri 8:00–18:00 CET).

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
