---
id: KB-048
category: account
lang: en
title: Making test payments
---

# Making test payments

Test payments let you check your integration end to end without moving any real money. They work only in the sandbox, which is a completely separate environment with its own Panel and its own keys.

## Before you start

Make sure you are working in the sandbox, not in production. The two environments do not share keys or data, so a request signed with production keys will never reach the sandbox and vice versa. Test payments never charge a card or transfer funds.

## Test cards and BLIK

You do not need your own card details to test. The sandbox Panel lists everything you need:

1. Sign in to your sandbox Panel.
2. Open the test data section.
3. Use the **test card numbers** provided there to simulate different outcomes, such as a completed or a failed payment.
4. Use the built-in **BLIK simulator** to run BLIK payments without a real banking app.

Because these are simulated instruments, they behave like the real thing in the flow — moving through statuses such as pending, authorized, and completed — but no charge is ever made.

## Important rules

- **Never test with a real card in production.** Production is for genuine customer payments; a real card there results in a real charge.
- Keep sandbox and production keys separate in your code and configuration so you do not mix environments by accident.

When your tests pass in the sandbox, switch your integration to production keys to go live. If you need help, contact us through a Panel ticket or at pomoc@kremzapay.demo, Monday to Friday, 8:00–18:00 CET.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
