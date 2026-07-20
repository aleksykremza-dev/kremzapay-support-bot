---
id: KB-065
category: refunds
lang: en
title: Bulk refunds from a file
---

# Bulk refunds from a file

When you need to refund many payments at once, you can upload them in a single file instead of processing each one by hand.

To run a bulk refund:

1. Open **Refunds** in the Panel and select **Import**.
2. Upload a CSV file with two columns: `sessionId` and `amount`.
3. Confirm the import to queue the refunds.

The `sessionId` is the identifier of the original payment. The `amount` is given in the smallest currency unit — grosze for PLN, so 25.00 PLN is entered as `2500`. This matches how amounts are handled in the API and avoids rounding mistakes.

Each file can contain up to 500 rows. If you have more refunds to process, split them across several files and import them one after another.

After you confirm, each row is processed individually and moves through the usual statuses: **created**, **processing**, and then **completed** or **rejected**. A row can fail on its own — for example, if the `sessionId` is unknown or the amount exceeds what remains refundable on that payment — without affecting the other rows.

Once processing finishes, a result report becomes available for download. It lists every row with its per-row status, so you can see exactly which refunds succeeded and which need attention. Refunded amounts are deducted from your next payout.

If any row is rejected and the reason is unclear, open a ticket in the Panel or email pomoc@kremzapay.demo (Mon–Fri, 8:00–18:00 CET).

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
