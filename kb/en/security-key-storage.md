---
id: KB-093
category: security
lang: en
title: Storing your API keys safely
---

# Storing your API keys safely

Your kremzaPay API keys authorise access to your account. Anyone who obtains a production key can act on your behalf, so treat keys like passwords and keep them out of any place that can be read by others.

Where keys should live:

1. In environment variables on your server, or
2. In a dedicated secret manager.

Where keys must never appear:

1. In repository code — never commit a key to Git, even a private repository.
2. In frontend code — anything running in the browser is visible to visitors.
3. In a mobile app — bundled apps can be unpacked and inspected.
4. In emails, chat messages or screenshots.

Keep sandbox and production keys separate. Use your sandbox key for development and testing, and switch to the production key only in your live environment. This prevents test code from accidentally moving real money and limits the damage if a development key leaks.

If you suspect a key has been exposed — for example it was pushed to a repository, shared in a message, or appeared in logs — rotate it immediately. Do not wait to confirm misuse.

To rotate a key:

1. Go to Settings → API keys in the Panel.
2. Select the affected key and choose Regenerate.
3. The old key stops working immediately, so update your server or secret manager with the new value right away to avoid interrupted payments.

Because regeneration invalidates the old key at once, plan a brief moment to deploy the new key. If you need help reviewing where a key may have been exposed, open a ticket in the Panel or write to pomoc@kremzapay.demo (Mon–Fri 8:00–18:00 CET).

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
