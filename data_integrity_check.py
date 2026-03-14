#!/usr/bin/env python3
"""
Run schema and data integrity checks against a disposable verification copy.
"""

import sqlite3

from my_app import db as app_db
from verification_helper import resolve_local_reference, verification_environment


REQUIRED_COLUMNS = {
    'vendors': {
        'id', 'name', 'email', 'phone', 'password', 'alternate_contact', 'shop_name',
        'goods_type', 'working_hours', 'street_area', 'photo_path', 'pincode', 'city',
        'location', 'is_approved', 'created_at', 'credits',
    },
    'wholesalers': {
        'id', 'name', 'phone', 'password', 'shop_name', 'id_doc_path', 'license_doc_path',
        'sourcing_info', 'location', 'is_approved', 'trust_score', 'response_rate',
        'delivery_rate', 'created_at', 'profile_photo',
    },
    'products': {
        'id', 'wholesaler_id', 'name', 'category', 'price', 'stock', 'group_buy_eligible',
        'image_path', 'views', 'likes', 'status', 'created_at',
    },
    'orders': {'id', 'wholesaler_id', 'vendor_id', 'total_amount', 'status', 'created_at'},
    'order_items': {'id', 'order_id', 'product_id', 'quantity', 'price', 'total'},
    'reviews': {'id', 'wholesaler_id', 'vendor_id', 'rating', 'comment', 'reply', 'created_at'},
    'analytics': {'id', 'wholesaler_id', 'date', 'total_orders', 'total_revenue', 'active_customers'},
    'donations': {'id', 'vendor_id', 'food_description', 'quantity', 'pickup_address', 'pickup_time', 'status', 'created_at'},
    'vendor_payment_methods': {'id', 'vendor_id', 'method_type', 'details', 'is_default', 'created_at'},
}

EXPECTED_FOREIGN_KEYS = {
    'products': {'wholesalers'},
    'orders': {'wholesalers', 'vendors'},
    'order_items': {'orders', 'products'},
    'reviews': {'wholesalers', 'vendors'},
    'analytics': {'wholesalers'},
    'donations': {'vendors'},
    'vendor_payment_methods': {'vendors'},
}

ORPHAN_CHECKS = {
    'products without a valid wholesaler': '''
        SELECT COUNT(*) FROM products
        WHERE wholesaler_id IS NOT NULL
          AND wholesaler_id NOT IN (SELECT id FROM wholesalers)
    ''',
    'orders without a valid vendor': '''
        SELECT COUNT(*) FROM orders
        WHERE vendor_id IS NOT NULL
          AND vendor_id NOT IN (SELECT id FROM vendors)
    ''',
    'orders without a valid wholesaler': '''
        SELECT COUNT(*) FROM orders
        WHERE wholesaler_id IS NOT NULL
          AND wholesaler_id NOT IN (SELECT id FROM wholesalers)
    ''',
    'order_items without a valid order': '''
        SELECT COUNT(*) FROM order_items
        WHERE order_id IS NOT NULL
          AND order_id NOT IN (SELECT id FROM orders)
    ''',
    'order_items without a valid product': '''
        SELECT COUNT(*) FROM order_items
        WHERE product_id IS NOT NULL
          AND product_id NOT IN (SELECT id FROM products)
    ''',
    'reviews without a valid vendor': '''
        SELECT COUNT(*) FROM reviews
        WHERE vendor_id IS NOT NULL
          AND vendor_id NOT IN (SELECT id FROM vendors)
    ''',
    'reviews without a valid wholesaler': '''
        SELECT COUNT(*) FROM reviews
        WHERE wholesaler_id IS NOT NULL
          AND wholesaler_id NOT IN (SELECT id FROM wholesalers)
    ''',
    'donations without a valid vendor': '''
        SELECT COUNT(*) FROM donations
        WHERE vendor_id IS NOT NULL
          AND vendor_id NOT IN (SELECT id FROM vendors)
    ''',
    'payment methods without a valid vendor': '''
        SELECT COUNT(*) FROM vendor_payment_methods
        WHERE vendor_id IS NOT NULL
          AND vendor_id NOT IN (SELECT id FROM vendors)
    ''',
}

VALUE_CHECKS = {
    'products with negative stock': 'SELECT COUNT(*) FROM products WHERE stock < 0',
    'products with non-positive prices': 'SELECT COUNT(*) FROM products WHERE price <= 0',
    'order_items with non-positive quantities': 'SELECT COUNT(*) FROM order_items WHERE quantity <= 0',
    'order_items with non-positive prices': 'SELECT COUNT(*) FROM order_items WHERE price <= 0',
    'order_items with non-positive totals': 'SELECT COUNT(*) FROM order_items WHERE total <= 0',
    'orders with negative totals': 'SELECT COUNT(*) FROM orders WHERE total_amount < 0',
}

FILE_REFERENCE_QUERIES = {
    'products.image_path': 'SELECT id, image_path FROM products WHERE image_path IS NOT NULL AND TRIM(image_path) <> ""',
    'vendors.photo_path': 'SELECT id, photo_path FROM vendors WHERE photo_path IS NOT NULL AND TRIM(photo_path) <> ""',
    'wholesalers.profile_photo': 'SELECT id, profile_photo FROM wholesalers WHERE profile_photo IS NOT NULL AND TRIM(profile_photo) <> ""',
    'wholesalers.id_doc_path': 'SELECT id, id_doc_path FROM wholesalers WHERE id_doc_path IS NOT NULL AND TRIM(id_doc_path) <> ""',
    'wholesalers.license_doc_path': 'SELECT id, license_doc_path FROM wholesalers WHERE license_doc_path IS NOT NULL AND TRIM(license_doc_path) <> ""',
}


def report(ok, message, failures):
    status = '[PASS]' if ok else '[FAIL]'
    print(f"{status} {message}")
    if not ok:
        failures.append(message)


def main():
    failures = []

    print("SAHAAYAK DATA INTEGRITY CHECK")
    print("=============================")

    with verification_environment(seed_fixture=True) as env:
        conn = sqlite3.connect(env.database_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        tables = {row[0] for row in cursor.fetchall()}

        for table_name, required_columns in REQUIRED_COLUMNS.items():
            report(table_name in tables, f"Table present: {table_name}", failures)
            if table_name not in tables:
                continue

            cursor.execute(f"PRAGMA table_info({table_name})")
            actual_columns = {row[1] for row in cursor.fetchall()}
            missing_columns = sorted(required_columns - actual_columns)
            report(
                not missing_columns,
                f"{table_name} required columns present",
                failures,
            )
            if missing_columns:
                print(f"       Missing columns: {', '.join(missing_columns)}")

        for table_name, expected_targets in EXPECTED_FOREIGN_KEYS.items():
            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            targets = {row[2] for row in cursor.fetchall()}
            missing_targets = sorted(expected_targets - targets)
            report(
                not missing_targets,
                f"{table_name} foreign key declarations present",
                failures,
            )
            if missing_targets:
                print(f"       Missing FK targets: {', '.join(missing_targets)}")

        for label, query in ORPHAN_CHECKS.items():
            cursor.execute(query)
            count = cursor.fetchone()[0]
            report(count == 0, f"{label}: {count}", failures)

        for label, query in VALUE_CHECKS.items():
            cursor.execute(query)
            count = cursor.fetchone()[0]
            report(count == 0, f"{label}: {count}", failures)

        cursor.execute(
            '''
            SELECT o.id, o.total_amount, COALESCE(SUM(oi.total), 0)
            FROM orders o
            LEFT JOIN order_items oi ON oi.order_id = o.id
            GROUP BY o.id
            HAVING ABS(COALESCE(o.total_amount, 0) - COALESCE(SUM(oi.total), 0)) > 0.01
            '''
        )
        mismatched_orders = cursor.fetchall()
        report(
            not mismatched_orders,
            f"orders.total_amount matches summed order_items totals ({len(mismatched_orders)} mismatches)",
            failures,
        )
        if mismatched_orders:
            for order_id, order_total, item_total in mismatched_orders:
                print(
                    f"       Order {order_id}: total_amount={order_total} item_sum={item_total}"
                )

        for label, query in FILE_REFERENCE_QUERIES.items():
            missing_paths = []
            cursor.execute(query)
            for row_id, raw_path in cursor.fetchall():
                resolved = resolve_local_reference(raw_path, env.static_dir)
                if resolved is not None and not resolved.exists():
                    missing_paths.append((row_id, raw_path, resolved))

            report(
                not missing_paths,
                f"{label} references existing local files ({len(missing_paths)} missing)",
                failures,
            )
            for row_id, raw_path, resolved in missing_paths[:5]:
                print(
                    f"       Row {row_id}: {raw_path} -> expected {resolved}"
                )

        with env.app.app_context():
            app_conn = app_db.get_connection()
            fk_state = app_conn.execute('PRAGMA foreign_keys').fetchone()[0]
            app_conn.close()

        report(
            fk_state == 1,
            f"app-style SQLite connections enable PRAGMA foreign_keys ({fk_state})",
            failures,
        )

        conn.close()

    if failures:
        print("")
        print("Integrity checks failed.")
        return 1

    print("")
    print("All integrity checks passed.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
