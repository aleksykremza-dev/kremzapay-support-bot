---
id: KB-073
category: integration
lang: en
title: Testing your connection
---

# Testing your connection

Before you register your first transaction, confirm that your credentials and base URL work together. kremzaPay provides a lightweight endpoint for exactly this check.

**The request**

Send a `GET` request to `/test-access` with your `api_key`. In the correct environment, with a valid key, the endpoint returns HTTP `200`. Any other response means the request did not reach a working, authorised connection.

**Use it as your first step**

Run this test before writing any payment logic. If `/test-access` does not return 200, there is no point in trying to register a transaction, because the same credentials and URL will fail there too. Confirming the connection first isolates configuration problems from integration bugs.

**What a non-200 response tells you**

- Check that the base URL and the `api_key` belong to the same environment. A production key against the sandbox URL (or the reverse) is the most common cause.
- Check that the `api_key` is copied exactly, with no extra whitespace.
- Check that you are calling the correct address: `api.sandbox.kremzapay.demo` for sandbox, `api.kremzapay.demo` for production.

**Use it in monitoring**

Beyond the initial setup, call `/test-access` periodically from your monitoring so you are alerted if the connection or credentials stop working in production. Keep in mind the rate limit of 100 requests per minute; requests above it receive HTTP 429, so space out monitoring checks sensibly.

If the test keeps failing after these checks, open a Panel ticket or email pomoc@kremzapay.demo.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
