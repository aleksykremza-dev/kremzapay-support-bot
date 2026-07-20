---
id: KB-068
category: integration
lang: en
title: API environments and addresses
---

# API environments and addresses

kremzaPay provides two separate API environments. Use the sandbox for development and testing, and production for live payments from real buyers.

**Addresses**

- Sandbox: `api.sandbox.kremzapay.demo`
- Production: `api.kremzapay.demo`

Each environment is fully isolated. Transactions, sessions, and reports created in the sandbox never appear in production and vice versa.

**Keys are per environment**

Every environment has its own set of credentials, including the API key and the crc_key used for signatures. Keys generated in the sandbox do not work in production. When you go live, generate a fresh production key set in the Panel under Settings and swap both the base URL and the keys.

**The most common mistake**

The single most frequent integration error is sending production keys to the sandbox URL (or the reverse). Because the environments are isolated, the request is rejected as unauthorized even though the key itself is valid. If you see authentication failures right after switching environments, check that the base URL and the key set belong to the same environment.

**Checklist before going live**

1. Replace the sandbox base URL with the production URL.
2. Replace the sandbox API key with the production API key.
3. Replace the sandbox crc_key with the production crc_key.
4. Run a test request (see the connection test article) against the production URL.

If a request fails, confirm the URL and key belong to the same environment before contacting support at pomoc@kremzapay.demo.

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
