# reset_database_phase4.py
# Complete database setup for Phase 4 with all dashboard features

import sqlite3
import os
from datetime import datetime, timedelta
import random

# Remove existing database
if os.path.exists('vendor_clubs.db'):
    os.remove('vendor_clubs.db')
    print("✅ Old database removed")

# Create new database with Phase 4 schema
conn = sqlite3.connect('vendor_clubs.db')
cursor = conn.cursor()

# Vendors table
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

# Enhanced Wholesalers table with performance metrics
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
        trust_score REAL DEFAULT 4.7,
        response_rate REAL DEFAULT 95.0,
        delivery_rate REAL DEFAULT 92.0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# Enhanced Products table
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
        views INTEGER DEFAULT 0,
        likes INTEGER DEFAULT 0,
        status TEXT DEFAULT 'In Stock',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (wholesaler_id) REFERENCES wholesalers (id)
    )
''')

# Orders table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wholesaler_id INTEGER,
        vendor_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        total_amount REAL,
        status TEXT DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (wholesaler_id) REFERENCES wholesalers (id),
        FOREIGN KEY (vendor_id) REFERENCES vendors (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
''')

# Reviews table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wholesaler_id INTEGER,
        vendor_id INTEGER,
        rating INTEGER,
        comment TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (wholesaler_id) REFERENCES wholesalers (id),
        FOREIGN KEY (vendor_id) REFERENCES vendors (id)
    )
''')

# Analytics table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wholesaler_id INTEGER,
        date DATE,
        total_orders INTEGER DEFAULT 0,
        total_revenue REAL DEFAULT 0,
        active_customers INTEGER DEFAULT 0,
        FOREIGN KEY (wholesaler_id) REFERENCES wholesalers (id)
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
    ('Neha Sharma', 'neha@example.com', '9876543217', 'vendor123', 'Kurla', True),
    ('Arjun Reddy', 'arjun@example.com', '9876543218', 'vendor123', 'Powai', True),
    ('Kavya Nair', 'kavya@example.com', '9876543219', 'vendor123', 'Malad', True),
]
cursor.executemany('INSERT INTO vendors (name, email, phone, password, location, is_approved) VALUES (?, ?, ?, ?, ?, ?)', vendors_data)

# Insert sample wholesaler with enhanced data
cursor.execute('''
    INSERT INTO wholesalers (name, phone, password, shop_name, sourcing_info, location, is_approved, trust_score, response_rate, delivery_rate)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', ('Mumbai Fresh Mart', '9999999999', 'password123', 'Fresh Mart Wholesale', 'Quality products from local farms and trusted suppliers', 'Ghatkopar', True, 4.7, 95.0, 92.0))

wholesaler_id = cursor.lastrowid

# Insert diverse sample products
products_data = [
    (wholesaler_id, 'Organic Tomatoes', 'Vegetables', 45.0, 500, True, 234, 12, 'In Stock'),
    (wholesaler_id, 'Fresh Spinach', 'Vegetables', 25.0, 200, True, 156, 8, 'Low Stock'),
    (wholesaler_id, 'Premium Carrots', 'Vegetables', 35.0, 0, True, 89, 5, 'Out of Stock'),
    (wholesaler_id, 'Red Onions', 'Vegetables', 30.0, 300, True, 312, 18, 'In Stock'),
    (wholesaler_id, 'Basmati Rice', 'Grains & Cereals', 85.0, 150, True, 445, 25, 'In Stock'),
    (wholesaler_id, 'Fresh Milk', 'Dairy Products', 55.0, 80, True, 198, 14, 'Low Stock'),
    (wholesaler_id, 'Green Chilies', 'Vegetables', 120.0, 45, True, 167, 9, 'Low Stock'),
    (wholesaler_id, 'Turmeric Powder', 'Spices & Condiments', 180.0, 120, True, 223, 16, 'In Stock'),
    (wholesaler_id, 'Coconut Oil', 'Packaged Foods', 320.0, 60, True, 134, 11, 'In Stock'),
    (wholesaler_id, 'Atta Flour', 'Grains & Cereals', 65.0, 220, True, 289, 19, 'In Stock'),
]
cursor.executemany('INSERT INTO products (wholesaler_id, name, category, price, stock, group_buy_eligible, views, likes, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', products_data)

# Generate realistic orders data
order_statuses = ['pending', 'processing', 'completed', 'completed', 'completed']  # More completed orders
orders_data = []

for i in range(50):  # Generate 50 orders
    vendor_id = random.randint(1, 10)
    product_id = random.randint(1, 10)
    quantity = random.randint(5, 100)
    
    # Get product price for total calculation
    cursor.execute('SELECT price FROM products WHERE id = ?', (product_id,))
    price = cursor.fetchone()[0]
    total_amount = quantity * price
    
    status = random.choice(order_statuses)
    
    # Generate orders over the last 30 days
    days_ago = random.randint(0, 30)
    order_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
    
    orders_data.append((wholesaler_id, vendor_id, product_id, quantity, total_amount, status, order_date))

cursor.executemany('INSERT INTO orders (wholesaler_id, vendor_id, product_id, quantity, total_amount, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)', orders_data)

# Insert sample reviews
reviews_data = [
    (wholesaler_id, 1, 5, 'Excellent quality vegetables, always fresh and delivered on time. Best wholesaler in Mumbai!'),
    (wholesaler_id, 2, 4, 'Good products and reliable supplier. Competitive pricing and fast response.'),
    (wholesaler_id, 3, 5, 'Outstanding service! Best wholesaler in the area. Highly recommended.'),
    (wholesaler_id, 4, 4, 'Quality products, but delivery could be faster. Overall satisfied.'),
    (wholesaler_id, 5, 5, 'Amazing variety and freshness. Customer service is top-notch.'),
    (wholesaler_id, 6, 4, 'Reliable supplier with consistent quality. Good for bulk orders.'),
    (wholesaler_id, 7, 5, 'Perfect for our restaurant needs. Fresh ingredients always available.'),
    (wholesaler_id, 8, 4, 'Good experience overall. Prices are competitive in the market.'),
]
cursor.executemany('INSERT INTO reviews (wholesaler_id, vendor_id, rating, comment) VALUES (?, ?, ?, ?)', reviews_data)

# Generate analytics data for the last 30 days
today = datetime.now()
analytics_data = []

for i in range(30):
    date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
    
    # Generate realistic daily numbers
    base_orders = 15
    daily_orders = base_orders + random.randint(-5, 10)
    daily_revenue = daily_orders * random.uniform(800, 1200)
    daily_customers = random.randint(5, 12)
    
    analytics_data.append((wholesaler_id, date, daily_orders, daily_revenue, daily_customers))

cursor.executemany('INSERT INTO analytics (wholesaler_id, date, total_orders, total_revenue, active_customers) VALUES (?, ?, ?, ?, ?)', analytics_data)

conn.commit()
conn.close()

print("✅ Phase 4 database created successfully!")
print("✅ Comprehensive sample data added")
print("\n📊 Database Contents:")
print("- 1 approved wholesaler with performance metrics")
print("- 10 approved vendors from different locations")
print("- 10 diverse products with views, likes, and stock status")
print("- 50 realistic orders with different statuses")
print("- 8 customer reviews with ratings")
print("- 30 days of analytics data")
print("\n📝 Test Credentials:")
print("Admin: admin / admin123")
print("Wholesaler: 9999999999 / password123")
print("Sample Vendor: 9876543210 / vendor123")
print("\n🚀 Run 'python app.py' to start Sahaayak with the complete dashboard!")
