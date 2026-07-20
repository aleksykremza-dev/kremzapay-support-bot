---
id: KB-074
category: integration
lang: en
title: E-commerce plugins
---

# E-commerce plugins

kremzaPay publishes official plugins for the most common online store platforms, so you can accept payments without writing integration code yourself. Supported platforms are WooCommerce, PrestaShop, Magento and Shopify.

## Installing a plugin

1. Open your platform's plugin marketplace (for example the WooCommerce plugin directory, the PrestaShop Addons marketplace, the Magento Marketplace or the Shopify App Store) and install the official kremzaPay plugin.
2. Activate the plugin in your store's admin area.
3. Open the plugin settings and enter three values from Panel → Settings: your `merchant_id`, `api_key` and `crc_key`. The `crc_key` is used to sign requests with SHA-384, so keep it confidential.
4. Choose the environment. Select the sandbox environment (`api.sandbox.kremzapay.demo`) while testing, and switch to production (`api.kremzapay.demo`) when you go live. Each environment uses its own set of keys.

## Test before going live

Before enabling payments for real customers, run a sandbox test payment. Place a test order in your store, complete it through the kremzaPay payment page and confirm that the order status updates correctly once the notification is received. Check that refunds and payment notifications also behave as expected.

If the status does not update, verify that your keys match the selected environment and that your store can receive webhook notifications. You can review notification delivery in Panel → Reports.

Keep the plugin updated to the latest version so you always have current payment methods and security fixes. If you need help, open a ticket in the Panel or write to pomoc@kremzapay.demo (Mon–Fri 8:00–18:00 CET).

---
*kremzaPay is a fictional payment provider. This page is demo documentation created for a portfolio project and has no legal or informational value.*
