---
id: KB-118
category: service
lang: en
title: Panel not loading
---

# Panel not loading

If the merchant Panel will not open or loads only partially, work through this checklist before reporting a problem. Most cases are resolved in the first few steps.

1. **Check the status page.** Open status.kremzapay.demo and look at the Panel component. If it shows a degraded or down state, the issue is on our side and already being worked on — no ticket needed.
2. **Try another browser or incognito window.** Opening the Panel in a different browser, or a private/incognito window, rules out extensions and cached files as the cause.
3. **Clear your cache.** A stale cache is a common reason the Panel loads incorrectly. Clear your browser cache and cookies for the site, then reload.
4. **Check 2FA time sync.** If you can reach the login screen but your two-factor code is rejected, make sure the clock on your phone is set to update automatically. A phone clock that has drifted will generate codes that no longer match.

**Your payments keep running**

Even when the Panel interface is unavailable, payment processing continues in the background. Transactions are still authorized and completed while the UI is down, so no payments are lost because you cannot open the Panel.

**Still not working?**

If the status page shows every component green and the Panel still will not load after the steps above, open a ticket from the Panel or by email. Include a screenshot of what you see and the time it happened (with timezone) so we can match it to our logs.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
