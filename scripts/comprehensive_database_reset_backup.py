# comprehensive_database_reset.py
# Complete database setup with multiple wholesalers and their specific products

import sqlite3
import os
from datetime import datetime, timedelta
import random

# Remove existing database
if os.path.exists('vendor_clubs.db'):
    os.remove('vendor_clubs.db')
    print("✅ Old database removed")

# Create new database with complete schema
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

# Enhanced Wholesalers table with performance metrics and profile photo
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
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        profile_photo TEXT
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

# Reviews table with reply functionality
cursor.execute('''
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wholesaler_id INTEGER,
        vendor_id INTEGER,
        rating INTEGER,
        comment TEXT,
        reply TEXT,
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

# Insert sample vendors from different areas
vendors_data = [
    ('Raj Patel', 'raj@example.com', '9876543210', 'vendor123', 'Ghatkopar', 1),
    ('Priya Shah', 'priya@example.com', '9876543211', 'vendor123', 'Ghatkopar', 1),
    ('Amit Kumar', 'amit@example.com', '9876543212', 'vendor123', 'Andheri', 1),
    ('Sunita Devi', 'sunita@example.com', '9876543213', 'vendor123', 'Andheri', 1),
    ('Ravi Singh', 'ravi@example.com', '9876543214', 'vendor123', 'Bandra', 1),
    ('Meera Joshi', 'meera@example.com', '9876543215', 'vendor123', 'Bandra', 1),
    ('Vikram Gupta', 'vikram@example.com', '9876543216', 'vendor123', 'Kurla', 1),
    ('Neha Sharma', 'neha@example.com', '9876543217', 'vendor123', 'Kurla', 1),
    ('Arjun Reddy', 'arjun@example.com', '9876543218', 'vendor123', 'Powai', 1),
    ('Kavya Nair', 'kavya@example.com', '9876543219', 'vendor123', 'Powai', 1),
    ('Deepak Jain', 'deepak@example.com', '9876543220', 'vendor123', 'Malad', 1),
    ('Rekha Iyer', 'rekha@example.com', '9876543221', 'vendor123', 'Malad', 1),
    ('Sanjay Desai', 'sanjay@example.com', '9876543222', 'vendor123', 'Borivali', 1),
    ('Pooja Agarwal', 'pooja@example.com', '9876543223', 'vendor123', 'Borivali', 1),
    ('Manoj Yadav', 'manoj@example.com', '9876543224', 'vendor123', 'Thane', 1),
]
cursor.executemany('INSERT INTO vendors (name, email, phone, password, location, is_approved) VALUES (?, ?, ?, ?, ?, ?)', vendors_data)

# Define locations for wholesalers
locations = ['Ghatkopar', 'Andheri', 'Bandra', 'Kurla', 'Powai', 'Malad', 'Borivali', 'Thane', 'Navi Mumbai']

# Insert the comprehensive list of wholesalers
wholesalers_data = [
    # Original wholesaler
    ('Mumbai Fresh Mart', '9999999999', 'password123', 'Fresh Mart Wholesale', 'Quality products from local farms and trusted suppliers across Maharashtra.', random.choice(locations), 1, round(random.uniform(4.5, 5.0), 1), round(random.uniform(90, 98), 1), round(random.uniform(88, 95), 1)),
    
    # New wholesalers
    ('Gupta Fresh Veggies', '9000000001', 'gupta123', 'Gupta Fresh Vegetable Market', 'Fresh vegetables sourced daily from local farms. Specializing in quality produce for street vendors.', random.choice(locations), 1, round(random.uniform(4.3, 4.9), 1), round(random.uniform(85, 95), 1), round(random.uniform(82, 90), 1)),
    
    ('Sharma Masala Bhandar', '9000000002', 'sharma123', 'Sharma Spice Wholesale', 'Premium quality spices and dry ingredients. Authentic flavors for your culinary needs.', random.choice(locations), 1, round(random.uniform(4.4, 4.8), 1), round(random.uniform(88, 96), 1), round(random.uniform(85, 92), 1)),
    
    ('Desai Dairy Depot', '9000000003', 'desai123', 'Desai Dairy Products', 'Fresh dairy products delivered daily. Quality milk, butter, and dairy alternatives.', random.choice(locations), 1, round(random.uniform(4.6, 5.0), 1), round(random.uniform(92, 98), 1), round(random.uniform(90, 95), 1)),
    
    ('Patil Pav Center', '9000000004', 'patil123', 'Patil Bakery Wholesale', 'Fresh bread, pav, and baked goods. Daily delivery of soft and fresh items.', random.choice(locations), 1, round(random.uniform(4.2, 4.7), 1), round(random.uniform(80, 90), 1), round(random.uniform(78, 88), 1)),
    
    ('Reddy ReadyServe', '9000000005', 'reddy123', 'Reddy Ready Foods', 'Pre-cooked and semi-prepared foods. Save time with our ready-to-serve items.', random.choice(locations), 1, round(random.uniform(4.3, 4.8), 1), round(random.uniform(85, 93), 1), round(random.uniform(83, 91), 1)),
    
    ('Khan Sauces & Oils', '9000000006', 'khan123', 'Khan Oil & Sauce House', 'Premium cooking oils, ghee, and authentic sauces. Quality ingredients for perfect taste.', random.choice(locations), 1, round(random.uniform(4.4, 4.9), 1), round(random.uniform(87, 94), 1), round(random.uniform(84, 90), 1)),
    
    ('Yadav Snacks Mart', '9000000007', 'yadav123', 'Yadav Snack Supplies', 'Crunchy snacks and dry goods. Perfect for chaat and snack preparations.', random.choice(locations), 1, round(random.uniform(4.1, 4.6), 1), round(random.uniform(82, 89), 1), round(random.uniform(80, 87), 1)),
    
    ('Joshi Beverage Supplies', '9000000008', 'joshi123', 'Joshi Beverage Center', 'Complete beverage solutions. Tea, coffee, and drink essentials for your business.', random.choice(locations), 1, round(random.uniform(4.3, 4.8), 1), round(random.uniform(86, 92), 1), round(random.uniform(82, 89), 1)),
    
    ('Sinha Packaging House', '9000000009', 'sinha123', 'Sinha Packaging Solutions', 'Eco-friendly packaging materials. Complete packaging solutions for food businesses.', random.choice(locations), 1, round(random.uniform(4.2, 4.7), 1), round(random.uniform(83, 90), 1), round(random.uniform(81, 88), 1)),
    
    ('Mehta Sweet Essentials', '9000000010', 'mehta123', 'Mehta Sweet Ingredients', 'Premium ingredients for sweets and desserts. Traditional flavors and quality assured.', random.choice(locations), 1, round(random.uniform(4.5, 4.9), 1), round(random.uniform(89, 95), 1), round(random.uniform(86, 92), 1)),
    
    ('Verma Green Cart', '9000000011', 'verma123', 'Verma Fresh Greens', 'Fresh herbs and leafy vegetables. Garden-fresh quality for your cooking needs.', random.choice(locations), 1, round(random.uniform(4.4, 4.8), 1), round(random.uniform(87, 93), 1), round(random.uniform(84, 91), 1)),
    
    ('Dixit Base & Ready Foods', '9000000012', 'dixit123', 'Dixit Food Solutions', 'Complete meal solutions and ready foods. Perfect base ingredients for quick preparation.', random.choice(locations), 1, round(random.uniform(4.3, 4.7), 1), round(random.uniform(85, 91), 1), round(random.uniform(82, 89), 1)),
]

for wholesaler in wholesalers_data:
    cursor.execute('''
        INSERT INTO wholesalers (name, phone, password, shop_name, sourcing_info, location, is_approved, trust_score, response_rate, delivery_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', wholesaler)

# Get all wholesaler IDs for product insertion
cursor.execute('SELECT id, name FROM wholesalers ORDER BY id')
wholesaler_info = cursor.fetchall()

# Define products for each wholesaler
wholesaler_products = {
    'Mumbai Fresh Mart': [
        ('Organic Tomatoes', 'Vegetables', 45.0, 500),
        ('Fresh Spinach', 'Vegetables', 25.0, 200),
        ('Premium Carrots', 'Vegetables', 35.0, 300),
        ('Red Onions', 'Vegetables', 30.0, 400),
        ('Basmati Rice', 'Grains & Cereals', 85.0, 150),
    ],
    'Gupta Fresh Veggies': [
        ('Potatoes', 'Vegetables', 25.0, 800),
        ('Tomatoes', 'Vegetables', 40.0, 600),
        ('Onions', 'Vegetables', 28.0, 700),
        ('Green Chillies', 'Vegetables', 120.0, 100),
        ('Cabbage', 'Vegetables', 20.0, 300),
        ('Lemon', 'Vegetables', 80.0, 200),
    ],
    'Sharma Masala Bhandar': [
        ('Red Chilli Powder', 'Spices & Condiments', 180.0, 150),
        ('Cumin (Jeera)', 'Spices & Condiments', 450.0, 80),
        ('Turmeric', 'Spices & Condiments', 160.0, 120),
        ('Garam Masala', 'Spices & Condiments', 320.0, 60),
        ('Hing (Asafoetida)', 'Spices & Condiments', 800.0, 25),
        ('Chaat Masala', 'Spices & Condiments', 280.0, 40),
    ],
    'Desai Dairy Depot': [
        ('Milk', 'Dairy Products', 55.0, 200),
        ('Butter', 'Dairy Products', 450.0, 80),
        ('Curd (Dahi)', 'Dairy Products', 60.0, 150),
        ('Paneer', 'Dairy Products', 320.0, 100),
        ('Condensed Milk', 'Dairy Products', 85.0, 120),
    ],
    'Patil Pav Center': [
        ('Pav', 'Packaged Foods', 35.0, 500),
        ('Buns', 'Packaged Foods', 40.0, 300),
        ('Bread Loaves', 'Packaged Foods', 30.0, 200),
        ('Roti/Paratha (Precooked)', 'Packaged Foods', 45.0, 150),
    ],
    'Reddy ReadyServe': [
        ('Boiled Potatoes', 'Packaged Foods', 50.0, 200),
        ('Ragda', 'Packaged Foods', 80.0, 100),
        ('Chole (Precooked)', 'Packaged Foods', 120.0, 80),
        ('Boiled Rice', 'Packaged Foods', 60.0, 150),
        ('Samosa Fillings', 'Packaged Foods', 100.0, 60),
    ],
    'Khan Sauces & Oils': [
        ('Vegetable Oil', 'Packaged Foods', 140.0, 300),
        ('Ghee', 'Dairy Products', 480.0, 100),
        ('Soy Sauce', 'Packaged Foods', 85.0, 80),
        ('Tamarind Pulp', 'Spices & Condiments', 90.0, 120),
        ('Green Chutney', 'Packaged Foods', 70.0, 150),
    ],
    'Yadav Snacks Mart': [
        ('Puffed Rice', 'Snacks & Beverages', 40.0, 200),
        ('Sev', 'Snacks & Beverages', 180.0, 100),
        ('Papdi', 'Snacks & Beverages', 160.0, 80),
        ('Nylon Sev', 'Snacks & Beverages', 220.0, 60),
        ('Boondi', 'Snacks & Beverages', 200.0, 70),
    ],
    'Joshi Beverage Supplies': [
        ('Tea Powder', 'Snacks & Beverages', 320.0, 150),
        ('Coffee', 'Snacks & Beverages', 450.0, 80),
        ('Sugar', 'Grains & Cereals', 45.0, 500),
        ('Soda', 'Snacks & Beverages', 25.0, 300),
        ('Lemon Concentrate', 'Snacks & Beverages', 120.0, 100),
    ],
    'Sinha Packaging House': [
        ('Paper Plates', 'Other', 15.0, 1000),
        ('Napkins', 'Other', 25.0, 800),
        ('Foil Containers', 'Other', 35.0, 500),
        ('Gloves', 'Other', 80.0, 200),
        ('Carry Bags', 'Other', 12.0, 1500),
    ],
    'Mehta Sweet Essentials': [
        ('Khoya / Mawa', 'Dairy Products', 380.0, 80),
        ('Sugar Syrup', 'Other', 60.0, 200),
        ('Vermicelli', 'Grains & Cereals', 85.0, 150),
        ('Rose Water', 'Other', 45.0, 100),
        ('Food Colors', 'Other', 25.0, 80),
    ],
    'Verma Green Cart': [
        ('Mint (Pudina)', 'Vegetables', 80.0, 100),
        ('Carrot', 'Vegetables', 35.0, 300),
        ('Coriander (Dhania)', 'Vegetables', 60.0, 150),
        ('Beetroot', 'Vegetables', 40.0, 200),
        ('Garlic', 'Vegetables', 180.0, 120),
    ],
    'Dixit Base & Ready Foods': [
        ('Pav', 'Packaged Foods', 35.0, 400),
        ('Ready Gravy Base', 'Packaged Foods', 150.0, 100),
        ('Chole (Precooked)', 'Packaged Foods', 120.0, 80),
        ('Boiled Potatoes', 'Packaged Foods', 50.0, 200),
        ('Tomato Ketchup', 'Packaged Foods', 85.0, 150),
    ],
}

# Insert products for each wholesaler
for wholesaler_id, wholesaler_name in wholesaler_info:
    if wholesaler_name in wholesaler_products:
        products = wholesaler_products[wholesaler_name]
        for product_name, category, price, stock in products:
            # Determine stock status
            if stock == 0:
                status = 'Out of Stock'
            elif stock < 50:
                status = 'Low Stock'
            else:
                status = 'In Stock'
            
            # Random views and likes
            views = random.randint(50, 500)
            likes = random.randint(5, 50)
            
            cursor.execute('''
                INSERT INTO products (wholesaler_id, name, category, price, stock, group_buy_eligible, views, likes, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (wholesaler_id, product_name, category, price, stock, 1, views, likes, status))

# Generate realistic orders across all wholesalers
cursor.execute('SELECT id FROM products')
all_product_ids = [row[0] for row in cursor.fetchall()]

cursor.execute('SELECT id FROM wholesalers')
all_wholesaler_ids = [row[0] for row in cursor.fetchall()]

order_statuses = ['pending', 'processing', 'completed', 'completed', 'completed']  # More completed orders
orders_data = []

for _ in range(200):  # Generate 200 orders across all wholesalers
    vendor_id = random.randint(1, 15)
    product_id = random.choice(all_product_ids)
    
    # Get wholesaler_id for this product
    cursor.execute('SELECT wholesaler_id, price FROM products WHERE id = ?', (product_id,))
    product_info = cursor.fetchone()
    wholesaler_id = product_info[0]
    price = product_info[1]
    
    quantity = random.randint(5, 100)
    total_amount = quantity * price
    status = random.choice(order_statuses)
    
    # Generate orders over the last 60 days
    days_ago = random.randint(0, 60)
    order_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
    
    orders_data.append((wholesaler_id, vendor_id, product_id, quantity, total_amount, status, order_date))

cursor.executemany('INSERT INTO orders (wholesaler_id, vendor_id, product_id, quantity, total_amount, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)', orders_data)

# Generate reviews for different wholesalers
review_comments = [
    "Excellent quality products, always fresh and delivered on time!",
    "Good supplier with competitive prices and reliable service.",
    "Outstanding quality! Best wholesaler in the area.",
    "Products are good but delivery could be faster.",
    "Amazing variety and freshness. Highly recommended!",
    "Reliable supplier with consistent quality.",
    "Perfect for our business needs. Great customer service.",
    "Good experience overall. Fair pricing.",
    "Fresh products always available when needed.",
    "Professional service and quality products.",
    "Best prices in the market with good quality.",
    "Quick response and helpful staff.",
]

replies = [
    "Thank you for your feedback! We appreciate your business.",
    "We're working on improving our delivery times.",
    "Thanks for choosing us! We value your trust.",
    "We're glad to serve your business needs.",
    "Your satisfaction is our priority. Thank you!",
    None,  # Some reviews without replies
    None,
    None,
]

reviews_data = []
for wholesaler_id in all_wholesaler_ids:
    # Generate 3-8 reviews per wholesaler
    num_reviews = random.randint(3, 8)
    for _ in range(num_reviews):
        vendor_id = random.randint(1, 15)
        rating = random.randint(3, 5)  # Mostly good ratings
        comment = random.choice(review_comments)
        reply = random.choice(replies)
        
        reviews_data.append((wholesaler_id, vendor_id, rating, comment, reply))

cursor.executemany('INSERT INTO reviews (wholesaler_id, vendor_id, rating, comment, reply) VALUES (?, ?, ?, ?, ?)', reviews_data)

# Generate analytics data for all wholesalers
today = datetime.now()
analytics_data = []

for wholesaler_id in all_wholesaler_ids:
    for i in range(30):  # Last 30 days
        date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        
        # Generate realistic daily numbers based on wholesaler size
        base_orders = random.randint(8, 25)
        daily_orders = base_orders + random.randint(-5, 10)
        daily_revenue = daily_orders * random.uniform(600, 1500)
        daily_customers = random.randint(3, 12)
        
        analytics_data.append((wholesaler_id, date, daily_orders, daily_revenue, daily_customers))

cursor.executemany('INSERT INTO analytics (wholesaler_id, date, total_orders, total_revenue, active_customers) VALUES (?, ?, ?, ?, ?)', analytics_data)

conn.commit()
conn.close()

print("✅ Comprehensive database created successfully!")
print("✅ All 13 wholesalers added with their specific products")
print("\n📊 Database Contents:")
print("- 13 approved wholesalers with unique specializations")
print("- 15 vendors from different Mumbai locations") 
print("- 60+ diverse products across all categories")
print("- 200 realistic orders with different statuses")
print("- 50+ customer reviews across all wholesalers")
print("- 30 days of analytics data for each wholesaler")

print("\n📝 Wholesaler Login Credentials:")
print("1. Mumbai Fresh Mart: 9999999999 / password123")
print("2. Gupta Fresh Veggies: 9000000001 / gupta123")
print("3. Sharma Masala Bhandar: 9000000002 / sharma123")
print("4. Desai Dairy Depot: 9000000003 / desai123")
print("5. Patil Pav Center: 9000000004 / patil123")
print("6. Reddy ReadyServe: 9000000005 / reddy123")
print("7. Khan Sauces & Oils: 9000000006 / khan123")
print("8. Yadav Snacks Mart: 9000000007 / yadav123")
print("9. Joshi Beverage Supplies: 9000000008 / joshi123")
print("10. Sinha Packaging House: 9000000009 / sinha123")
print("11. Mehta Sweet Essentials: 9000000010 / mehta123")
print("12. Verma Green Cart: 9000000011 / verma123")
print("13. Dixit Base & Ready Foods: 9000000012 / dixit123")

print("\n🎯 Admin Credentials:")
print("Admin: admin / admin123")

print("\n🚀 Run 'python app.py' to start Sahaayak with comprehensive data!")
