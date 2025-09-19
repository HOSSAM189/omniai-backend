# USD Payment System Setup Guide

## ❌ Critical Issues (Must Fix)

1. Stripe authentication failed - check secret key
2. Error validating Stripe account: Invalid API Key provided: sk_test_***********************here

## ⚠️ Warnings (Recommended to Fix)

1. Could not fully validate USD support: Invalid API Key provided: sk_test_***********************here
2. Could not validate webhook configuration: Invalid API Key provided: sk_test_***********************here

## ✅ Configured Correctly

1. STRIPE_SECRET_KEY is configured
2. STRIPE_PUBLISHABLE_KEY is configured
3. STRIPE_WEBHOOK_SECRET is configured
4. PAYMENT_CURRENCY is configured: USD
5. PAYMENT_CURRENCY_ENFORCEMENT is configured: strict
6. MAX_PAYMENT_AMOUNT is configured: 10000.00
7. MIN_PAYMENT_AMOUNT is configured: 1.00
8. Webhook secret format appears correct
9. Payment amount limits: $1.00 - $10000.00
10. Fraud detection enabled
11. Payment rate limit: 10 requests per window

## Environment Variables Template

```bash
# Required Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# USD Payment Configuration
PAYMENT_CURRENCY=USD
PAYMENT_CURRENCY_ENFORCEMENT=strict
ALLOWED_CURRENCIES=USD

# Security Settings
MAX_PAYMENT_AMOUNT=10000.00
MIN_PAYMENT_AMOUNT=1.00
ENABLE_FRAUD_DETECTION=True
PAYMENT_RATE_LIMIT=10
```

## Stripe Account Setup Checklist

1. ✅ Create Stripe account
2. ✅ Verify business information
3. ✅ Enable card payments capability
4. ✅ Set default currency to USD
5. ✅ Configure webhook endpoints
6. ✅ Test with USD transactions
7. ✅ Enable live mode for production

