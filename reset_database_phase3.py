# reset_database_phase3.py
# Run this script to reset your database for Phase 3

import sqlite3
import os
from datetime import datetime, timedelta

# Remove existing database
if os.path.exists('vendor_clubs.db'):
    os.remove('vendor_clubs.db')
    print("✅ Old database removed")

# Create new database with Phase 3 schema
conn = sqlite3.connect('vendor_clubs.db')
cursor = conn.cursor()

# Updated vendors table (no more clubs dependency)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS vendors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        password TEXT,
        location TEXT,
        is_approved BOOLEAN DEFAULT FALSE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# Wholesalers table with password
cursor.execute('''
    CREATE TABLE IF NOT EXISTS wholesalers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        shop_name TEXT NOT NULL,
        id_doc_path TEXT,
        license_doc_path TEXT,
        sourcing_info TEXT,
        location TEXT,
        is_approved BOOLEAN DEFAULT FALSE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# Products table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wholesaler_id INTEGER,
        name TEXT NOT NULL,
        category TEXT,
        price REAL NOT NULL,
        stock INTEGER NOT NULL,
        group_buy_eligible BOOLEAN DEFAULT TRUE,
        image_path TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (wholesaler_id) REFERENCES wholesalers (id)
    )
''')

# Buying groups table (new for Phase 3)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS buying_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        product_id INTEGER,
        target_quantity INTEGER,
        current_quantity INTEGER DEFAULT 0,
        price_per_unit REAL,
        deadline DATE,
        status TEXT DEFAULT 'active',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
''')

# Group orders table (new for Phase 3)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS group_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER,
        vendor_id INTEGER,
        quantity INTEGER,
        total_price REAL,
        status TEXT DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (group_id) REFERENCES buying_groups (id),
        FOREIGN KEY (vendor_id) REFERENCES vendors (id)
    )
''')

# Insert sample vendors
vendors_data = [
    ('Raj Patel', 'raj@example.com', '9876543210', 'vendor123', 'Ghatkopar', True),
    ('Priya Shah', 'priya@example.com', '9876543211', 'vendor123', 'Ghatkopar', True),
    ('Amit Kumar', 'amit@example.com', '9876543212', 'vendor123', 'Ghatkopar', True),
    ('Sunita Devi', 'sunita@example.com', '9876543213', 'vendor123', 'Andheri', True),
    ('Ravi Singh', 'ravi@example.com', '9876543214', 'vendor123', 'Andheri', True),
    ('Meera Joshi', 'meera@example.com', '9876543215', 'vendor123', 'Bandra', True),
    ('Vikram Gupta', 'vikram@example.com', '9876543216', 'vendor123', 'Bandra', True),
]
cursor.executemany('INSERT INTO vendors (name, email, phone, password, location, is_approved) VALUES (?, ?, ?, ?, ?, ?)', vendors_data)

# Add sample approved wholesaler
cursor.execute('''
    INSERT INTO wholesalers (name, phone, password, shop_name, sourcing_info, location, is_approved)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', ('Mumbai Fresh Mart', '9999999999', 'password123', 'Fresh Mart Wholesale', 'Quality products from local farms', 'Ghatkopar', True))

wholesaler_id = cursor.lastrowid

# Add sample products
products_data = [
    (wholesaler_id, 'Fresh Tomatoes', 'Vegetables', 45.0, 500, True),
    (wholesaler_id, 'Red Onions', 'Vegetables', 35.0, 300, True),
    (wholesaler_id, 'Basmati Rice', 'Grains & Cereals', 85.0, 200, True),
    (wholesaler_id, 'Fresh Milk', 'Dairy Products', 55.0, 100, True),
    (wholesaler_id, 'Green Chilies', 'Vegetables', 120.0, 50, True),
]
cursor.executemany('INSERT INTO products (wholesaler_id, name, category, price, stock, group_buy_eligible) VALUES (?, ?, ?, ?, ?, ?)', products_data)

# Add sample buying groups
today = datetime.now()
deadline = today + timedelta(days=7)

buying_groups_data = [
    ('Ghatkopar Tomato Group', 1, 100, 45, 40.0, deadline.strftime('%Y-%m-%d'), 'active'),
    ('Andheri Rice Collective', 3, 50, 25, 80.0, deadline.strftime('%Y-%m-%d'), 'active'),
    ('Bandra Onion Club', 2, 80, 60, 32.0, deadline.strftime('%Y-%m-%d'), 'active'),
]
cursor.executemany('INSERT INTO buying_groups (name, product_id, target_quantity, current_quantity, price_per_unit, deadline, status) VALUES (?, ?, ?, ?, ?, ?, ?)', buying_groups_data)

# Add sample group orders
group_orders_data = [
    (1, 1, 20, 800.0, 'pending'),  # Raj ordered 20 tomatoes
    (1, 2, 15, 600.0, 'pending'),  # Priya ordered 15 tomatoes  
    (1, 3, 10, 400.0, 'pending'),  # Amit ordered 10 tomatoes
    (2, 4, 15, 1200.0, 'pending'), # Sunita ordered 15 rice
    (2, 5, 10, 800.0, 'pending'),  # Ravi ordered 10 rice
    (3, 6, 25, 800.0, 'pending'),  # Meera ordered 25 onions
    (3, 7, 35, 1120.0, 'pending'), # Vikram ordered 35 onions
]
cursor.executemany('INSERT INTO group_orders (group_id, vendor_id, quantity, total_price, status) VALUES (?, ?, ?, ?, ?)', group_orders_data)

conn.commit()
conn.close()

print("✅ Phase 3 database created successfully!")
print("✅ Sample data added")
print("\n📝 Test Credentials:")
print("Admin: admin / admin123")
print("Sample Wholesaler: 9999999999 / password123")
print("Sample Vendor: 9876543210 / vendor123")
print("\n🏪 Sample Data:")
print("- 1 approved wholesaler with 5 products")
print("- 7 approved vendors")
print("- 3 active buying groups with orders")
print("\n🚀 Run 'python app.py' to start Sahaayak!")
