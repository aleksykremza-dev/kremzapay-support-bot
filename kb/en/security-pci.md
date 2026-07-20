---
id: KB-090
category: security
lang: en
title: PCI DSS and your shop
---

# PCI DSS and your shop

PCI DSS is the security standard that applies to any business that stores, processes or transmits payment card data. Many merchants assume this means heavy audits and expensive infrastructure. In most cases, it does not — because with kremzaPay your shop never touches card numbers at all.

When a buyer pays by card, the card details are entered on kremzaPay's own payment page or widget. The data goes straight to kremzaPay and is processed on our side. Your shop receives only the payment identifier and its status (pending, authorized, completed, failed or expired). Card numbers, expiry dates and security codes never reach your servers.

This keeps a typical shop out of the most demanding parts of PCI scope. You are not holding sensitive card data, so you are not responsible for protecting it in your own systems.

To keep it that way, follow a few simple rules:

1. Never build your own card form. Always send buyers to the kremzaPay payment page or embed the official widget.
2. Never ask customers to send card numbers by email, chat or phone, and never store them in your database, logs or spreadsheets.
3. Keep your integration limited to the identifiers and statuses kremzaPay returns.

If a plugin, theme or third-party tool tries to collect raw card data inside your own checkout, treat that as a red flag and stop using it.

If you are unsure whether part of your setup pulls card data into your systems, open a ticket in the Panel or write to pomoc@kremzapay.demo (Mon–Fri 8:00–18:00 CET) and we will help you review it.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
