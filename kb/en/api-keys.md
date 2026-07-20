---
id: KB-011
category: integration
lang: en
title: Where to find your merchant_id, api_key and crc_key
---

# Where to find your merchant_id, api_key and crc_key

Every integration with kremzaPay relies on three values. You will find all of them in the Panel.

## Where to look

1. Log in to the kremzaPay Panel.
2. Open **Settings**.
3. Select the **API keys** tab.

The page lists the keys for the environment you are currently in. Sandbox and production keys are different, so make sure you copy the set that matches the environment your code targets.

## What each value means

- **merchant_id** — the numeric identifier of your shop. It tells kremzaPay which account a request belongs to.
- **api_key** — authorizes REST API calls. Send it with every request to the API.
- **crc_key** — used only to build request signatures. It is never sent as a plain field in a request; it goes into the signature hash instead.

## Keeping keys safe

- Never share your keys with anyone outside your team.
- Never commit keys to a code repository, public or private. Store them in environment variables or a secrets manager.
- Keep sandbox and production keys separated in your configuration so a test key can never reach production.

If a key may have been exposed, contact support so it can be rotated. You can open a ticket from the Panel or email pomoc@kremzapay.demo (Mon–Fri 8:00–18:00 CET).

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
