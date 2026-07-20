---
id: KB-091
category: security
lang: en
title: How kremzaPay anti-fraud works
---

# How kremzaPay anti-fraud works

Every payment processed through kremzaPay passes through automatic risk scoring before it can complete. The goal is simple: stop fraudulent transactions while letting genuine buyers pay without friction.

The scoring engine looks at a wide range of signals in real time. These include:

1. Velocity checks — how many attempts come from the same card, buyer or device in a short window.
2. Geographic and device signals — the location, device and network behind the payment, and whether they fit the expected pattern.
3. Card behaviour — repeated failures, unusual amounts or combinations that often indicate testing or stolen cards.

For card payments judged to be risky, kremzaPay enforces 3DS2 authentication. The buyer is asked to confirm the payment with their bank, which moves liability and adds a strong verification step. Low-risk payments may pass without that extra step.

When a payment scores too high, it does not complete. In the Panel you will see it end with the status `failed`. The buyer is asked to try another method or contact their bank.

For security reasons, kremzaPay does not disclose why a specific payment was scored as risky or which signals triggered a decision. Publishing that logic would help fraudsters work around it. Merchants therefore see only the final status — `pending`, `authorized`, `completed`, `failed` or `expired` — not the internal reasoning.

You do not need to configure anything for anti-fraud to run; it is always active. If you believe legitimate payments are being blocked unusually often, open a ticket in the Panel or write to pomoc@kremzapay.demo (Mon–Fri 8:00–18:00 CET) with the affected payment identifiers and we will review the pattern.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
