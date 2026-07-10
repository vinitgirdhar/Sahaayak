#!/usr/bin/env python3
"""
Validate the disposable verification fixture used by the pre-deployment checks.
"""

from verification_helper import (
    VERIFICATION_PRODUCTS,
    VERIFICATION_VENDOR,
    VERIFICATION_WHOLESALERS,
    fetch_fixture_snapshot,
    verification_environment,
)


def main():
    failures = []

    print("SAHAAYAK VERIFICATION FIXTURE CHECK")
    print("==================================")

    with verification_environment(seed_fixture=True) as env:
        snapshot = fetch_fixture_snapshot(env.database_path)

        vendor = snapshot['vendor']
        if not vendor:
            failures.append('verification vendor is missing')
        else:
            print(f"[PASS] Vendor present: {vendor[0]} ({vendor[1]})")
            if vendor[1] != VERIFICATION_VENDOR['phone']:
                failures.append('verification vendor phone does not match the fixture')
            if vendor[2] != VERIFICATION_VENDOR['location']:
                failures.append('verification vendor location does not match the fixture')
            if vendor[3] != VERIFICATION_VENDOR['is_approved']:
                failures.append('verification vendor approval flag does not match the fixture')

        wholesaler_rows = snapshot['wholesalers']
        wholesaler_by_phone = {row[1]: row for row in wholesaler_rows}
        for wholesaler in VERIFICATION_WHOLESALERS:
            row = wholesaler_by_phone.get(wholesaler['phone'])
            if not row:
                failures.append(f"wholesaler fixture missing for {wholesaler['phone']}")
                continue

            print(
                f"[PASS] Wholesaler present: {row[0]} ({row[1]}) "
                f"approved={row[3]}"
            )
            if row[0] != wholesaler['name']:
                failures.append(f"wholesaler name mismatch for {wholesaler['phone']}")
            if row[2] != wholesaler['shop_name']:
                failures.append(f"wholesaler shop_name mismatch for {wholesaler['phone']}")
            if row[3] != wholesaler['is_approved']:
                failures.append(f"wholesaler approval mismatch for {wholesaler['phone']}")

        product_rows = snapshot['products']
        product_lookup = {(row[0], row[1]): row for row in product_rows}
        for product in VERIFICATION_PRODUCTS:
            key = (product['wholesaler_phone'], product['name'])
            row = product_lookup.get(key)
            if not row:
                failures.append(
                    f"product fixture missing for {product['name']} ({product['wholesaler_phone']})"
                )
                continue

            print(
                f"[PASS] Product present: {row[1]} under wholesaler {row[0]} "
                f"price={row[3]} stock={row[4]}"
            )
            if row[2] != product['category']:
                failures.append(f"product category mismatch for {product['name']}")
            if float(row[3]) != float(product['price']):
                failures.append(f"product price mismatch for {product['name']}")
            if int(row[4]) != int(product['stock']):
                failures.append(f"product stock mismatch for {product['name']}")

        fixture_image = env.static_dir / 'uploads' / 'groceries.jpg'
        if fixture_image.exists():
            print(f"[PASS] Fixture image present: {fixture_image}")
        else:
            failures.append('fixture image is missing from the copied static directory')

    if failures:
        print("")
        print("FAILURES")
        print("--------")
        for failure in failures:
            print(f"[FAIL] {failure}")
        return 1

    print("")
    print("All verification fixture checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
