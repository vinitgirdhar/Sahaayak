#!/usr/bin/env python3
"""
Exercise current Flask routes against a disposable verification environment.
"""

import sqlite3
from unittest.mock import Mock, patch

from verification_helper import (
    VERIFICATION_PRODUCTS,
    VERIFICATION_VENDOR,
    VERIFICATION_WHOLESALERS,
    extract_local_static_refs,
    live_gemini_enabled,
    resolve_local_reference,
    verification_environment,
)


class Suite:
    def __init__(self):
        self.failures = []
        self.passes = 0

    def check(self, condition, message, detail=None):
        status = '[PASS]' if condition else '[FAIL]'
        print(f"{status} {message}")
        if condition:
            self.passes += 1
            return

        self.failures.append(message)
        if detail:
            print(f"       {detail}")


def fetch_ids(database_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    ids = {}
    cursor.execute('SELECT id FROM vendors WHERE phone = ?', (VERIFICATION_VENDOR['phone'],))
    ids['vendor_id'] = cursor.fetchone()[0]

    wholesaler_ids = {}
    for wholesaler in VERIFICATION_WHOLESALERS:
        cursor.execute('SELECT id FROM wholesalers WHERE phone = ?', (wholesaler['phone'],))
        row = cursor.fetchone()
        wholesaler_ids[wholesaler['phone']] = row[0] if row else None
    ids['wholesaler_ids'] = wholesaler_ids

    product_ids = {}
    for product in VERIFICATION_PRODUCTS:
        cursor.execute(
            '''
            SELECT p.id
            FROM products p
            JOIN wholesalers w ON w.id = p.wholesaler_id
            WHERE w.phone = ? AND p.name = ?
            ''',
            (product['wholesaler_phone'], product['name']),
        )
        row = cursor.fetchone()
        product_ids[product['name']] = row[0] if row else None
    ids['product_ids'] = product_ids

    conn.close()
    return ids


def scan_local_static_refs(suite, response, static_dir, label):
    if response.status_code != 200 or 'text/html' not in response.content_type:
        return

    refs = extract_local_static_refs(response.get_data(as_text=True))
    missing = []
    for ref in refs:
        resolved = resolve_local_reference(ref, static_dir)
        if resolved is not None and not resolved.exists():
            missing.append((ref, resolved))

    suite.check(
        not missing,
        f"{label} local static references resolve ({len(refs)} refs scanned)",
        detail=', '.join(f"{ref} -> {resolved}" for ref, resolved in missing[:5]),
    )


def require_redirect(suite, response, expected_suffix, message):
    location = response.headers.get('Location', '')
    suite.check(
        response.status_code == 302 and location.endswith(expected_suffix),
        message,
        detail=f"status={response.status_code} location={location}",
    )


def main():
    suite = Suite()

    print("SAHAAYAK USER FLOW CHECK")
    print("========================")

    with verification_environment(seed_fixture=True) as env:
        ids = fetch_ids(env.database_path)
        anonymous_client = env.app.test_client()
        vendor_client = env.app.test_client()
        wholesaler_client = env.app.test_client()

        smoke_pages = [
            ('/', anonymous_client),
            ('/vendor/login', anonymous_client),
            ('/vendor/register', anonymous_client),
            ('/wholesaler/login', anonymous_client),
            ('/register-wholesaler', anonymous_client),
        ]
        for path, client in smoke_pages:
            response = client.get(path)
            suite.check(response.status_code == 200, f"GET {path} returns 200", detail=f"status={response.status_code}")
            scan_local_static_refs(suite, response, env.static_dir, f"GET {path}")

        ai_unauthorized = anonymous_client.post('/api/ask-ai', json={'product_name': 'Potato'})
        suite.check(
            ai_unauthorized.status_code == 401,
            '/api/ask-ai rejects anonymous requests',
            detail=f"status={ai_unauthorized.status_code}",
        )

        vendor_registration = vendor_client.post(
            '/vendor/register',
            data={
                'name': 'Verification Vendor Two',
                'phone': '9000000002',
                'password': 'verifyvendor2',
                'alternate_contact': '9000000012',
                'email': 'verification.vendor.two@example.com',
                'shop_name': 'Verification Cart Two',
                'goods_type': 'Beverages',
                'working_hours': '07:00-15:00',
                'street_area': 'Verification Lane',
                'pincode': '400002',
                'city': 'Mumbai',
                'location': 'Andheri',
            },
            follow_redirects=False,
        )
        require_redirect(
            suite,
            vendor_registration,
            '/vendor/login',
            'vendor registration redirects to vendor login',
        )

        duplicate_vendor = vendor_client.post(
            '/vendor/register',
            data={
                'name': 'Duplicate Verification Vendor',
                'phone': VERIFICATION_VENDOR['phone'],
                'password': 'duplicate',
                'alternate_contact': '9000000098',
                'email': 'duplicate@example.com',
                'shop_name': 'Duplicate Cart',
                'goods_type': 'Snacks',
                'working_hours': '05:00-12:00',
                'street_area': 'Duplicate Market',
                'pincode': '400003',
                'city': 'Mumbai',
                'location': 'Kurla',
            },
            follow_redirects=False,
        )
        require_redirect(
            suite,
            duplicate_vendor,
            '/vendor/register',
            'duplicate vendor registration redirects back to registration',
        )

        bad_vendor_login = vendor_client.post(
            '/vendor/login',
            data={'phone': VERIFICATION_VENDOR['phone'], 'password': 'wrong-password'},
            follow_redirects=True,
        )
        suite.check(
            bad_vendor_login.status_code == 200 and 'Invalid credentials' in bad_vendor_login.get_data(as_text=True),
            'vendor login rejects invalid credentials',
        )

        vendor_login = vendor_client.post(
            '/vendor/login',
            data={'phone': VERIFICATION_VENDOR['phone'], 'password': VERIFICATION_VENDOR['password']},
            follow_redirects=False,
        )
        require_redirect(
            suite,
            vendor_login,
            '/vendor/dashboard',
            'vendor login redirects to dashboard',
        )

        vendor_pages = [
            ('/vendor/dashboard', 'Our Categories'),
            ('/vendor/category/dry-ingredients', VERIFICATION_PRODUCTS[0]['name']),
            ('/vendor/cart', 'My Cart'),
        ]
        for path, marker in vendor_pages:
            response = vendor_client.get(path)
            body = response.get_data(as_text=True)
            suite.check(
                response.status_code == 200 and marker in body,
                f"GET {path} renders expected vendor content",
                detail=f"status={response.status_code}",
            )
            scan_local_static_refs(suite, response, env.static_dir, f"GET {path}")

        product_alpha = ids['product_ids'][VERIFICATION_PRODUCTS[0]['name']]
        product_beta = ids['product_ids'][VERIFICATION_PRODUCTS[1]['name']]

        add_alpha = vendor_client.post(
            '/vendor/add-to-cart',
            data={'product_id': product_alpha, 'quantity': 2},
        )
        suite.check(
            add_alpha.status_code == 200 and add_alpha.get_json().get('success'),
            'vendor can add first product to cart',
            detail=str(add_alpha.get_json()),
        )

        add_beta = vendor_client.post(
            '/vendor/add-to-cart',
            data={'product_id': product_beta, 'quantity': 1},
        )
        suite.check(
            add_beta.status_code == 200 and add_beta.get_json().get('cart_count') == 3,
            'vendor can add second wholesaler product to cart',
            detail=str(add_beta.get_json()),
        )

        cart_count = vendor_client.get('/vendor/get-cart-count')
        cart_count_json = cart_count.get_json()
        suite.check(
            cart_count.status_code == 200 and cart_count_json.get('count') == 3,
            'cart count endpoint reports accumulated quantity',
            detail=str(cart_count_json),
        )

        cart_view = vendor_client.get('/vendor/cart/get')
        cart_view_json = cart_view.get_json()
        suite.check(
            cart_view.status_code == 200 and cart_view_json.get('count') == 3 and len(cart_view_json.get('cart', [])) == 2,
            'cart get endpoint returns both cart items',
            detail=str(cart_view_json),
        )

        update_cart = vendor_client.post(
            '/vendor/update-cart',
            data={'product_id': product_alpha, 'quantity': 1},
        )
        update_cart_json = update_cart.get_json()
        suite.check(
            update_cart.status_code == 200 and update_cart_json.get('totals', {}).get('total_items') == 2,
            'cart update endpoint recalculates totals',
            detail=str(update_cart_json),
        )

        remove_beta = vendor_client.post(
            '/vendor/remove-from-cart',
            data={'product_id': str(product_beta)},
        )
        suite.check(
            remove_beta.status_code == 200 and remove_beta.get_json().get('cart_count') == 1,
            'vendor can remove an item from the cart',
            detail=str(remove_beta.get_json()),
        )

        sync_cart = vendor_client.post(
            '/vendor/cart/sync',
            json={
                'cart': [
                    {'id': product_alpha, 'quantity': 1},
                    {'id': product_beta, 'quantity': 1},
                ]
            },
        )
        sync_cart_json = sync_cart.get_json()
        suite.check(
            sync_cart.status_code == 200 and sync_cart_json.get('synced_items') == 2,
            'cart sync endpoint accepts frontend-style payloads',
            detail=str(sync_cart_json),
        )

        checkout_page = vendor_client.get('/vendor/checkout')
        checkout_body = checkout_page.get_data(as_text=True)
        suite.check(
            checkout_page.status_code == 200
            and VERIFICATION_PRODUCTS[0]['name'] in checkout_body
            and VERIFICATION_PRODUCTS[1]['name'] in checkout_body,
            'checkout page renders split-cart contents',
            detail=f"status={checkout_page.status_code}",
        )
        scan_local_static_refs(suite, checkout_page, env.static_dir, 'GET /vendor/checkout')

        checkout_submit = vendor_client.post(
            '/vendor/checkout',
            data={
                'payment_method': 'cod',
                'delivery_address': 'Verification Address, Mumbai - 400001',
            },
            follow_redirects=False,
        )
        require_redirect(
            suite,
            checkout_submit,
            '/vendor/order-confirmation',
            'checkout redirects to order confirmation',
        )

        with vendor_client.session_transaction() as session_state:
            last_order_ids = list(session_state.get('last_order_ids', []))
        suite.check(
            len(last_order_ids) == 2,
            'checkout stores one order id per wholesaler in session',
            detail=str(last_order_ids),
        )

        conn = sqlite3.connect(env.database_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT o.id, o.total_amount, o.status, w.phone AS wholesaler_phone
            FROM orders o
            JOIN wholesalers w ON w.id = o.wholesaler_id
            WHERE o.id IN (?, ?)
            ORDER BY w.phone
            ''',
            tuple(last_order_ids),
        )
        orders = cursor.fetchall()
        suite.check(
            len(orders) == 2,
            'checkout created two persisted orders',
            detail=f"orders_found={len(orders)}",
        )

        order_totals = {}
        for order in orders:
            cursor.execute(
                'SELECT product_id, quantity, total FROM order_items WHERE order_id = ?',
                (order['id'],),
            )
            items = cursor.fetchall()
            order_totals[order['wholesaler_phone']] = (order['total_amount'], items)

        alpha_total, alpha_items = order_totals[VERIFICATION_PRODUCTS[0]['wholesaler_phone']]
        beta_total, beta_items = order_totals[VERIFICATION_PRODUCTS[1]['wholesaler_phone']]
        suite.check(
            len(alpha_items) == 1 and round(float(alpha_total), 2) == round(VERIFICATION_PRODUCTS[0]['price'], 2),
            'first wholesaler order stores correct totals',
            detail=f"total={alpha_total} items={alpha_items}",
        )
        suite.check(
            len(beta_items) == 1 and round(float(beta_total), 2) == round(VERIFICATION_PRODUCTS[1]['price'], 2),
            'second wholesaler order stores correct totals',
            detail=f"total={beta_total} items={beta_items}",
        )
        conn.close()

        order_confirmation = vendor_client.get('/vendor/order-confirmation')
        suite.check(
            order_confirmation.status_code == 200 and 'Verification Address' in order_confirmation.get_data(as_text=True),
            'order confirmation page renders last checkout metadata',
            detail=f"status={order_confirmation.status_code}",
        )
        scan_local_static_refs(suite, order_confirmation, env.static_dir, 'GET /vendor/order-confirmation')

        vendor_orders_page = vendor_client.get('/vendor/orders')
        vendor_orders_body = vendor_orders_page.get_data(as_text=True)
        suite.check(
            vendor_orders_page.status_code == 200 and VERIFICATION_WHOLESALERS[0]['name'] in vendor_orders_body,
            'vendor orders page lists created orders',
            detail=f"status={vendor_orders_page.status_code}",
        )
        scan_local_static_refs(suite, vendor_orders_page, env.static_dir, 'GET /vendor/orders')

        order_detail = vendor_client.get(f"/vendor/order/{last_order_ids[0]}")
        suite.check(
            order_detail.status_code == 200 and 'Order' in order_detail.get_data(as_text=True),
            'vendor order detail renders successfully',
            detail=f"status={order_detail.status_code}",
        )
        scan_local_static_refs(suite, order_detail, env.static_dir, f"GET /vendor/order/{last_order_ids[0]}")

        filter_products = vendor_client.post(
            '/api/filter-products',
            json={'maxBudget': 200, 'category': 'All Categories', 'sortBy': 'Price Low to High', 'limit': 5},
        )
        filtered_json = filter_products.get_json()
        suite.check(
            filter_products.status_code == 200
            and isinstance(filtered_json, list)
            and filtered_json
            and {'name', 'price', 'wholesaler_name'} <= set(filtered_json[0].keys()),
            '/api/filter-products returns the expected product shape',
            detail=str(filtered_json[:1]),
        )

        sort_wholesalers = vendor_client.post('/api/sort-wholesalers', json={'sort_by': 'price'})
        sort_json = sort_wholesalers.get_json()
        suite.check(
            sort_wholesalers.status_code == 200
            and isinstance(sort_json, list)
            and sort_json
            and {'id', 'name', 'avg_price'} <= set(sort_json[0].keys()),
            '/api/sort-wholesalers returns wholesaler cards',
            detail=str(sort_json[:1]),
        )

        beta_wholesaler_id = ids['wholesaler_ids'][VERIFICATION_PRODUCTS[1]['wholesaler_phone']]
        wholesaler_filter = vendor_client.post(
            f'/api/wholesaler/{beta_wholesaler_id}/filter-products',
            json={'category': 'All Categories', 'sortBy': 'Price: Low to High'},
        )
        wholesaler_filter_json = wholesaler_filter.get_json()
        suite.check(
            wholesaler_filter.status_code == 200
            and isinstance(wholesaler_filter_json, list)
            and wholesaler_filter_json
            and {'id', 'name', 'price', 'status'} <= set(wholesaler_filter_json[0].keys()),
            'wholesaler-specific filter endpoint returns product rows',
            detail=str(wholesaler_filter_json[:1]),
        )

        ai_missing_product = vendor_client.post('/api/ask-ai', json={})
        suite.check(
            ai_missing_product.status_code == 400,
            '/api/ask-ai requires a product name',
            detail=str(ai_missing_product.get_json()),
        )

        if live_gemini_enabled():
            ai_success = vendor_client.post('/api/ask-ai', json={'product_name': 'Potato'})
            ai_json = ai_success.get_json()
            suite.check(
                ai_success.status_code == 200 and bool(ai_json.get('response')),
                '/api/ask-ai live smoke returns content',
                detail=str(ai_json),
            )
        else:
            mocked_response = Mock()
            mocked_response.text = (
                "Price: INR 20-30/kg\n"
                "Trend: Stable\n"
                "Demand: High\n"
                "Profit: 20-30% margin\n"
                "Tip: Buy early in the mandi"
            )
            with patch('my_app.routes.genai.configure') as configure_mock, patch(
                'my_app.routes.genai.GenerativeModel'
            ) as model_mock:
                model_mock.return_value.generate_content.return_value = mocked_response
                ai_success = vendor_client.post('/api/ask-ai', json={'product_name': 'Potato'})
                ai_json = ai_success.get_json()
                suite.check(
                    ai_success.status_code == 200 and 'Price:' in ai_json.get('response', ''),
                    '/api/ask-ai mocked smoke returns structured content',
                    detail=str(ai_json),
                )
                suite.check(
                    configure_mock.called and model_mock.called,
                    '/api/ask-ai configures and instantiates the Gemini client in mocked mode',
                )

        pending_login = wholesaler_client.post(
            '/wholesaler/login',
            data={
                'phone': VERIFICATION_WHOLESALERS[2]['phone'],
                'password': VERIFICATION_WHOLESALERS[2]['password'],
            },
            follow_redirects=True,
        )
        suite.check(
            pending_login.status_code == 200
            and 'pending approval' in pending_login.get_data(as_text=True).lower(),
            'pending wholesaler login is rejected with the expected message',
        )

        wholesaler_login = wholesaler_client.post(
            '/wholesaler/login',
            data={
                'phone': VERIFICATION_WHOLESALERS[0]['phone'],
                'password': VERIFICATION_WHOLESALERS[0]['password'],
            },
            follow_redirects=False,
        )
        require_redirect(
            suite,
            wholesaler_login,
            '/wholesaler/dashboard',
            'approved wholesaler login redirects to dashboard',
        )

        wholesaler_pages = [
            ('/wholesaler/dashboard', 'Dashboard'),
            ('/wholesaler/products', 'Manage Products'),
            ('/wholesaler/orders', 'Manage Orders'),
            ('/wholesaler/profile', 'Profile'),
            ('/wholesaler/add-product', 'Add New Product'),
        ]
        for path, marker in wholesaler_pages:
            response = wholesaler_client.get(path)
            body = response.get_data(as_text=True)
            suite.check(
                response.status_code == 200 and marker in body,
                f"GET {path} renders expected wholesaler content",
                detail=f"status={response.status_code}",
            )
            scan_local_static_refs(suite, response, env.static_dir, f"GET {path}")

        add_product = wholesaler_client.post(
            '/wholesaler/add-product',
            data={
                'main_category': 'Grains & Cereals',
                'name': 'Verification New Product',
                'price': '55.00',
                'stock': '60',
            },
            follow_redirects=False,
        )
        require_redirect(
            suite,
            add_product,
            '/wholesaler/dashboard',
            'wholesaler add-product redirects back to dashboard',
        )

        conn = sqlite3.connect(env.database_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, stock, status FROM products WHERE name = ?', ('Verification New Product',))
        added_product = cursor.fetchone()
        suite.check(
            added_product is not None and added_product[1] == 60 and added_product[2] == 'In Stock',
            'added product was persisted with expected stock and status',
            detail=str(added_product),
        )

        edit_product_page = wholesaler_client.get(f'/wholesaler/edit-product/{added_product[0]}')
        suite.check(
            edit_product_page.status_code == 200 and 'Edit Product' in edit_product_page.get_data(as_text=True),
            'edit-product page loads for the newly added product',
            detail=f"status={edit_product_page.status_code}",
        )
        scan_local_static_refs(
            suite,
            edit_product_page,
            env.static_dir,
            f"GET /wholesaler/edit-product/{added_product[0]}",
        )

        edit_product = wholesaler_client.post(
            f'/wholesaler/edit-product/{added_product[0]}',
            data={
                'main_category': 'Grains & Cereals',
                'name': 'Verification New Product Updated',
                'price': '65.00',
                'stock': '25',
            },
            follow_redirects=False,
        )
        require_redirect(
            suite,
            edit_product,
            '/wholesaler/products',
            'edit-product redirects back to products listing',
        )
        cursor.execute('SELECT name, price, stock, status FROM products WHERE id = ?', (added_product[0],))
        edited_product = cursor.fetchone()
        suite.check(
            edited_product == ('Verification New Product Updated', 65.0, 25, 'Low Stock'),
            'edited product updates name, price, stock, and status',
            detail=str(edited_product),
        )

        update_stock = wholesaler_client.post(
            '/api/update-stock',
            json={'product_id': added_product[0], 'stock': 0},
        )
        suite.check(
            update_stock.status_code == 200 and update_stock.get_json().get('status') == 'Out of Stock',
            'update-stock API recalculates product status',
            detail=str(update_stock.get_json()),
        )

        delete_product = wholesaler_client.post(
            '/api/delete-product',
            json={'product_id': added_product[0]},
        )
        suite.check(
            delete_product.status_code == 200 and delete_product.get_json().get('success'),
            'delete-product API removes the product',
            detail=str(delete_product.get_json()),
        )
        cursor.execute('SELECT COUNT(*) FROM products WHERE id = ?', (added_product[0],))
        suite.check(
            cursor.fetchone()[0] == 0,
            'deleted product no longer exists in the database',
        )

        alpha_order_id = None
        for order in orders:
            if order['wholesaler_phone'] == VERIFICATION_PRODUCTS[0]['wholesaler_phone']:
                alpha_order_id = order['id']
                break
        conn.close()

        update_order_status = wholesaler_client.post(
            '/api/update-order-status',
            json={'order_id': alpha_order_id, 'status': 'completed'},
        )
        suite.check(
            update_order_status.status_code == 200 and update_order_status.get_json().get('success'),
            'update-order-status API accepts wholesaler status changes',
            detail=str(update_order_status.get_json()),
        )

        vendor_orders_after_update = vendor_client.get('/vendor/orders')
        suite.check(
            vendor_orders_after_update.status_code == 200
            and 'Completed' in vendor_orders_after_update.get_data(as_text=True),
            'vendor orders page reflects updated wholesaler order status',
            detail=f"status={vendor_orders_after_update.status_code}",
        )
        scan_local_static_refs(
            suite,
            vendor_orders_after_update,
            env.static_dir,
            'GET /vendor/orders after status update',
        )

    print("")
    print(f"Checks passed: {suite.passes}")
    if suite.failures:
        print(f"Checks failed: {len(suite.failures)}")
        return 1

    print("All user flow checks passed.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
