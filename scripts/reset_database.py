# reset_database.py
# Run this script to reset your database with the new schema

import sqlite3
import os

# Remove existing database
if os.path.exists('vendor_clubs.db'):
    os.remove('vendor_clubs.db')
    print("✅ Old database removed")

# Create new database with updated schema
conn = sqlite3.connect('vendor_clubs.db')
cursor = conn.cursor()

# Create tables with new schema
cursor.execute('''
    CREATE TABLE IF NOT EXISTS clubs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS vendors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        club_id INTEGER,
        location TEXT,
        FOREIGN KEY (club_id) REFERENCES clubs (id)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS cart_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        club_id INTEGER,
        item_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        estimated_price REAL,
        FOREIGN KEY (club_id) REFERENCES clubs (id)
    )
''')

# Updated wholesalers table with password field
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

# Insert sample data
clubs_data = [
    ('Ghatkopar Chaat Sellers',),
    ('Andheri Fruit Vendors',),
    ('Bandra Snack Coalition',)
]
cursor.executemany('INSERT INTO clubs (name) VALUES (?)', clubs_data)

vendors_data = [
    ('Raj Patel', 'raj@example.com', 1, 'Ghatkopar'),
    ('Priya Shah', 'priya@example.com', 1, 'Ghatkopar'),
    ('Amit Kumar', 'amit@example.com', 1, 'Ghatkopar'),
    ('Sunita Devi', 'sunita@example.com', 2, 'Andheri'),
    ('Ravi Singh', 'ravi@example.com', 2, 'Andheri'),
    ('Meera Joshi', 'meera@example.com', 3, 'Bandra'),
    ('Vikram Gupta', 'vikram@example.com', 3, 'Bandra'),
]
cursor.executemany('INSERT INTO vendors (name, email, club_id, location) VALUES (?, ?, ?, ?)', vendors_data)

cart_items_data = [
    (1, 'Onions (kg)', 50, 2500.0),
    (1, 'Tomatoes (kg)', 30, 1800.0),
    (1, 'Potatoes (kg)', 40, 2000.0),
    (1, 'Green Chilies (kg)', 10, 800.0),
    (2, 'Apples (kg)', 25, 3750.0),
    (2, 'Bananas (dozen)', 20, 1200.0),
    (2, 'Oranges (kg)', 35, 2800.0),
    (3, 'Bread (loaves)', 40, 1200.0),
    (3, 'Milk (liters)', 30, 1800.0),
    (3, 'Butter (kg)', 15, 4500.0),
]
cursor.executemany('INSERT INTO cart_items (club_id, item_name, quantity, estimated_price) VALUES (?, ?, ?, ?)', cart_items_data)

# Add a sample wholesaler for testing
cursor.execute('''
    INSERT INTO wholesalers (name, phone, password, shop_name, sourcing_info, location, is_approved)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', ('Test Wholesaler', '9999999999', 'password123', 'Test Shop', 'Quality products from local farms', 'Ghatkopar', True))

conn.commit()
conn.close()

print("✅ Database reset successfully!")
print("✅ Sample data added")
print("\n📝 Test Credentials:")
print("Admin: admin / admin123")
print("Sample Wholesaler: 9999999999 / password123")
print("\n🚀 Run 'python app.py' to start the application")
