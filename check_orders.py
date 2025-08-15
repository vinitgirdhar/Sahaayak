import sqlite3

# Connect to the database
conn = sqlite3.connect('vendor_clubs.db')
cursor = conn.cursor()

# Check the SQL query used in vendor_orders route
print('Checking the SQL query used in vendor_orders route:')
cursor.execute("""
    SELECT o.*, p.name as product_name, w.name as wholesaler_name, w.phone as wholesaler_phone
    FROM orders o 
    JOIN products p ON o.product_id = p.id 
    JOIN wholesalers w ON o.wholesaler_id = w.id 
    WHERE o.vendor_id = 1 
    ORDER BY o.created_at DESC
""")
orders_with_join = cursor.fetchall()
print(f'Found {len(orders_with_join)} orders with JOIN query')

# Print all orders with column indices
for order_idx, order in enumerate(orders_with_join):
    print(f'\nOrder #{order_idx+1}:')
    for i, value in enumerate(order):
        print(f'Column {i}: {value}')
    print(f'Wholesaler name (order[9]): {order[9]}')
    print(f'Product name (order[8]): {order[8]}')
    # Check if there's a column 11
    if len(order) > 11:
        print(f'Column 11 (expected wholesaler_name): {order[11]}')
    else:
        print(f'No column 11 exists, total columns: {len(order)}')

conn.close()