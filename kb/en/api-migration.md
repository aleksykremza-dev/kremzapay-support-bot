---
id: KB-080
category: integration
lang: en
title: Migrating between API versions
---

# Migrating between API versions

kremzaPay versions its API so we can add features and improve behaviour without breaking existing integrations. The current version is v2. Version v1 is deprecated and will be retired.

## Sunset policy

When a version is scheduled for removal, its sunset date is announced at least 6 months in advance. You are notified in two ways: by email to your registered contact address, and through a banner shown in the Panel. This gives you a predictable window to complete your migration before v1 stops working.

## Planning your migration

1. Confirm which version your integration currently uses.
2. Review what changed between versions. The full list of changes is published in Panel → Reports → API changelog. Read it to see which endpoints, fields and behaviours differ in v2.
3. Update your integration to the v2 endpoints and adjust any request or response handling that changed.

## Testing during the transition

The sandbox environment (`api.sandbox.kremzapay.demo`) supports both versions during the transition period, so you can test your v2 integration without disrupting your live v1 traffic. Run a complete set of test payments, refunds and webhook notifications against v2 in the sandbox before switching production over.

Once you are confident, move your production traffic (`api.kremzapay.demo`) to v2. Keep an eye on the Panel banner and email announcements so you complete the switch before the v1 sunset date.

If anything in the changelog is unclear or a migration step fails, open a ticket in the Panel or write to pomoc@kremzapay.demo (Mon–Fri 8:00–18:00 CET).

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
