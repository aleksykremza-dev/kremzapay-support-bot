---
id: KB-119
category: service
lang: en
title: Webhooks not arriving — checklist
---

# Webhooks not arriving — checklist

If your server is not receiving webhook notifications, work through this checklist in order. Most delivery problems come from a configuration or server-response issue that these steps will surface.

1. **Check the status page.** Open status.kremzapay.demo and look at the Webhooks component. If it shows a degraded or down state, delivery is delayed on our side and no action is needed from you.
2. **Verify your notification URL.** In Panel → Settings → Notifications, confirm the notification URL is correct and points to a **public HTTPS** endpoint. Local addresses and non-HTTPS URLs cannot receive webhooks.
3. **Reply 200 "OK" quickly.** Your endpoint must respond with HTTP **200** and the body **"OK"** in under 10 seconds. Slow responses are treated as failures and trigger retries.
4. **Allow our IP range.** Make sure your firewall permits the IP range listed in Panel → Settings → Notifications. If those addresses are blocked, notifications never reach your server.
5. **Check retries in the payment view.** Open the affected payment in the Panel to see delivery attempts. kremzaPay makes up to 8 retries over 24 hours, so a temporarily unreachable server will be retried.
6. **Use the resend button.** For a specific payment, use the resend button in the payment view to trigger delivery again after you have fixed the cause.

**Still nothing?**

If webhooks still do not arrive after all six steps, open a ticket from the Panel. Include the sessionId of an affected payment and the relevant timestamps so we can trace delivery on our side.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
