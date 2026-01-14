import sqlite3

conn = sqlite3.connect('vendor_clubs.db')
cur = conn.cursor()

print('=== COMPREHENSIVE DATA INTEGRITY CHECK ===\n')

# Check vendors - schema: id, name, email, phone, password, alternate_contact, shop_name, goods_type, working_hours, street_area, photo_path, pincode, city, location, is_approved, created_at, credits
print('--- VENDORS ---')
cur.execute('SELECT id, name, phone, email, shop_name FROM vendors')
vendors = cur.fetchall()
print(f'Total vendors: {len(vendors)}')
for v in vendors:
    issues = []
    if not v[1]: issues.append('missing name')
    if not v[2]: issues.append('missing phone')
    if not v[3]: issues.append('missing email')
    if issues:
        print(f'  Vendor {v[0]}: {issues}')
    else:
        print(f'  Vendor {v[0]}: {v[1]} ({v[4]}) - OK')

# Check wholesalers - schema: id, name, phone, password, shop_name, id_doc_path, license_doc_path, sourcing_info, location, is_approved, trust_score, response_rate, delivery_rate, created_at, profile_photo
print('\n--- WHOLESALERS ---')
cur.execute('SELECT id, name, phone, shop_name, is_approved FROM wholesalers')
wholesalers = cur.fetchall()
print(f'Total wholesalers: {len(wholesalers)}')
for w in wholesalers:
    issues = []
    if not w[1]: issues.append('missing name')
    if not w[2]: issues.append('missing phone')
    if not w[3]: issues.append('missing shop_name')
    status = 'approved' if w[4] else 'pending'
    if issues:
        print(f'  Wholesaler {w[0]}: {issues}')
    else:
        print(f'  Wholesaler {w[0]}: {w[3]} ({status}) - OK')

# Check products for data integrity - schema: id, wholesaler_id, name, category, price, stock, group_buy_eligible, image_path, views, likes, status, created_at, image_prompt
print('\n--- PRODUCTS DATA QUALITY ---')
cur.execute('SELECT id, name, price, stock, category, image_path, wholesaler_id FROM products')
products = cur.fetchall()
issues_count = {'no_image': 0, 'zero_stock': 0, 'invalid_price': 0, 'no_category': 0}
for p in products:
    if not p[5] or p[5] == '': issues_count['no_image'] += 1
    if p[3] == 0: issues_count['zero_stock'] += 1
    if not p[2] or p[2] <= 0: issues_count['invalid_price'] += 1
    if not p[4] or p[4] == '': issues_count['no_category'] += 1

print(f"Products without images: {issues_count['no_image']}/{len(products)}")
print(f"Products with zero stock: {issues_count['zero_stock']}/{len(products)}")
print(f"Products with invalid price: {issues_count['invalid_price']}/{len(products)}")
print(f"Products without category: {issues_count['no_category']}/{len(products)}")

# Check orders
print('\n--- ORDERS ---')
cur.execute('SELECT COUNT(*) FROM orders')
order_count = cur.fetchone()[0]
print(f'Total orders: {order_count}')

# Check for orphan records
print('\n--- ORPHAN RECORDS CHECK ---')
cur.execute('SELECT COUNT(*) FROM products WHERE wholesaler_id NOT IN (SELECT id FROM wholesalers)')
orphan_products = cur.fetchone()[0]
print(f'Products with invalid wholesaler_id: {orphan_products}')

cur.execute('SELECT COUNT(*) FROM orders WHERE vendor_id NOT IN (SELECT id FROM vendors)')
orphan_orders = cur.fetchone()[0]
print(f'Orders with invalid vendor_id: {orphan_orders}')

# Check table schema
print('\n--- DATABASE TABLES ---')
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
for t in tables:
    cur.execute(f'SELECT COUNT(*) FROM {t[0]}')
    count = cur.fetchone()[0]
    print(f'  {t[0]}: {count} records')

conn.close()
print('\n=== DATA INTEGRITY CHECK COMPLETE ===')
