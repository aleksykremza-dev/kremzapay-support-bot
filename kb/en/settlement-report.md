---
id: KB-020
category: payouts
lang: en
title: Reading the settlement report
---

# Reading the settlement report

Every payout has a settlement report that shows exactly how the transferred amount was calculated. You can find these reports in the kremzaPay Panel under Reports.

## What the report contains

Each settlement report covers a single payout and includes:

- **Gross amount** — the sum of all payments included in the payout.
- **Commission** — the fee deducted according to your agreement.
- **Net amount** — the gross amount minus commission and any refunds. This is the figure that is actually transferred to your bank account.

The relationship is straightforward:

`Net = Gross − Commission − Refunds`

## Payment rows

The report lists every payment that makes up the payout. Each payment row carries its own `sessionId`, which lets you match a line in the report to the corresponding transaction in your own records. Use this identifier when reconciling your books or investigating a specific payment.

## Exporting

You can export any settlement report as a CSV file for accounting or reconciliation. The CSV contains the same rows and identifiers shown in the Panel, so it can be imported directly into your bookkeeping tools.

If a figure in a report is unclear, open a ticket from the Panel or email pomoc@kremzapay.demo (Mon–Fri 8:00–18:00 CET), quoting the payout and the relevant sessionId.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
