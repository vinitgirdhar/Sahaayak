# Sahaayak Manual Verification Checklist

Run this browser pass after the automated scripts complete.

## Viewports

- Desktop: `1440x900`
- Mobile: `390x844`

## Pages To Check

- `/`
- `/vendor/register`
- `/vendor/login`
- `/vendor/dashboard`
- `/vendor/category/dry-ingredients`
- `/vendor/cart`
- `/vendor/checkout`
- `/vendor/orders`
- `/wholesaler/login`
- `/wholesaler/dashboard`
- `/wholesaler/products`
- `/wholesaler/add-product`
- `/wholesaler/edit-product/<existing-product-id>`
- `/wholesaler/orders`
- `/wholesaler/profile`

## What To Verify

- No overlapping or clipped content.
- Desktop-to-mobile layout changes keep navigation usable.
- Buttons, links, drawers, and forms remain clickable.
- Local images and icons load without 404s.
- Cart, checkout, and order status screens show consistent totals and labels.
- Floating/mobile navigation does not cover primary actions or form fields.

## Evidence To Capture

- Screenshot each key page once on desktop and once on mobile.
- Save at least one screenshot for any broken alignment, overflow, or missing asset.
- Note the exact route, viewport, and action that triggered each issue.
