---
id: KB-084
category: payouts
lang: en
title: Exporting reports (CSV)
---

# Exporting reports (CSV)

kremzaPay lets you export your transaction and settlement data as a CSV file, ready for accounting or reconciliation.

To export a report:

1. Open **Reports** in your panel.
2. Click **Export**.
3. Choose a **date range** for the data you need.
4. Optionally apply the **per-shop filter** to limit the export to a single shop.
5. Confirm to download the file.

The exported CSV includes the following columns:

- **sessionId** — the unique identifier used to match each payment to your order.
- **amount** — the transaction value.
- **currency** — one of PLN, EUR, USD, GBP, or CZK.
- **status** — the payment status (for example `completed`, `pending`, `failed`).
- **payout id** — the payout the row was settled in.

File format details:

- Encoding is **UTF-8**, so Polish characters and other accented text display correctly.
- Values are **semicolon-separated** (`;`), which matches the regional convention and imports cleanly into most spreadsheet tools.

If you export regularly, you can automate the download instead of doing it by hand. The **API report endpoint** returns the same data programmatically, so you can pull reports on a schedule and feed them straight into your accounting or reconciliation process.

When opening the file in a spreadsheet application, make sure it reads the file as UTF-8 with a semicolon delimiter so columns align correctly.

If a column looks empty or misaligned, or an expected row is missing from the export, raise a ticket in the panel or email pomoc@kremzapay.demo (Mon–Fri, 8:00–18:00 CET).

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
