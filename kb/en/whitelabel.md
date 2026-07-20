---
id: KB-077
category: integration
lang: en
title: White-label payment page
---

# White-label payment page

The white-label payment page lets you serve the kremzaPay payment page from your own custom domain, such as `pay.yourshop.example`, instead of a kremzaPay address. Buyers see your domain throughout the payment, which reinforces trust and keeps the checkout consistent with your brand. This option is available per agreement, so it must be arranged with kremzaPay before you set it up.

## Requirements

- **Agreement** — the white-label domain must be enabled for your account under your service agreement.
- **DNS setup** — you create a DNS record that points your chosen subdomain (for example `pay.yourshop.example`) to the target provided by kremzaPay.
- **Certificate** — a valid TLS certificate must cover the domain so the payment page is served over HTTPS. Depending on your agreement the certificate is either issued for you or supplied by you.

## Setting it up

1. Confirm the white-label option is active for your account.
2. Add the DNS record for your subdomain as instructed.
3. Ensure the certificate is in place and the domain resolves over HTTPS.
4. Verify that the payment page opens correctly on your domain.

## Branding

Any branding you configure in Settings → Branding — such as your logo and colours — applies automatically to the white-label page. Update those settings first so the page matches your store before you direct real customers to it.

Test a sandbox payment on the custom domain before going live to confirm the certificate, redirect and notifications all work end to end. If you need help, open a ticket in the Panel or write to pomoc@kremzapay.demo (Mon–Fri 8:00–18:00 CET).

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
