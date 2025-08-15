# comprehensive_database_reset.py
# Complete database setup with multiple wholesalers and their specific products

import sqlite3
import os
import json
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

# Vendor Payment Methods table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS vendor_payment_methods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_id INTEGER NOT NULL,
        method_type TEXT NOT NULL, -- 'upi' or 'card'
        details TEXT NOT NULL, -- JSON string with details like UPI ID or card info
        is_default BOOLEAN DEFAULT FALSE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (vendor_id) REFERENCES vendors (id)
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
    ('Mumbai Fresh Mart', '9999999999', 'password123', 'Fresh Mart Wholesale', 'Quality products from local farms and trusted suppliers across Maharashtra.', random.choice(locations), 1, round(random.uniform(4.5, 5.0), 1), round(random.uniform(90, 98), 1), round(random.uniform(88, 95), 1)),
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

# --- UPDATED PRODUCT DATA ---
wholesaler_products = {
    'Mumbai Fresh Mart': [
        ('Broccoli', 'Vegetables', 90.00, 150), ('Cauliflower', 'Vegetables', 45.00, 200),
        ('Bottle Gourd (Lauki)', 'Vegetables', 35.00, 250), ('Brinjal (Baingan)', 'Vegetables', 40.00, 180),
        ('Sweet Corn', 'Vegetables', 60.00, 300), ('Lady Finger (Bhindi)', 'Vegetables', 55.00, 220),
        ('Zucchini', 'Vegetables', 120.00, 100), ('Drumstick (Moringa)', 'Vegetables', 80.00, 120),
        ('Capsicum (Green)', 'Vegetables', 70.00, 180), ('Pumpkin', 'Vegetables', 50.00, 160),
    ],
    'Gupta Fresh Veggies': [
        ('Baby Potatoes', 'Vegetables', 45.00, 300), ('Spring Onions', 'Vegetables', 40.00, 150),
        ('Red Capsicum', 'Vegetables', 90.00, 120), ('Yellow Capsicum', 'Vegetables', 95.00, 110),
        ('Cherry Tomatoes', 'Vegetables', 140.00, 80), ('Green Peas', 'Vegetables', 120.00, 200),
        ('Turnip', 'Vegetables', 35.00, 130), ('Radish', 'Vegetables', 30.00, 140),
        ('Snake Gourd', 'Vegetables', 60.00, 90), ('Ash Gourd', 'Vegetables', 55.00, 85),
    ],
    'Sharma Masala Bhandar': [
        ('Coriander Powder', 'Spices & Condiments', 140.00, 100), ('Black Pepper (Whole)', 'Spices & Condiments', 550.00, 50),
        ('Mustard Seeds', 'Spices & Condiments', 90.00, 120), ('Curry Leaves (Dried)', 'Spices & Condiments', 80.00, 80),
        ('Fennel Seeds (Saunf)', 'Spices & Condiments', 160.00, 90), ('Fenugreek Seeds (Methi)', 'Spices & Condiments', 100.00, 70),
        ('Ajwain (Carom Seeds)', 'Spices & Condiments', 120.00, 60), ('Cloves (Laung)', 'Spices & Condiments', 600.00, 40),
        ('Cardamom (Elaichi)', 'Spices & Condiments', 800.00, 30), ('Cinnamon Sticks', 'Spices & Condiments', 500.00, 45),
    ],
    'Desai Dairy Depot': [
        ('Fresh Cream', 'Dairy Products', 120.00, 80), ('Cheese Slices', 'Dairy Products', 150.00, 100),
        ('Mozzarella Cheese', 'Dairy Products', 380.00, 60), ('Ghee (Organic)', 'Dairy Products', 520.00, 50),
        ('Yogurt (Flavored)', 'Dairy Products', 70.00, 120), ('Buttermilk', 'Dairy Products', 40.00, 150),
        ('Malai Paneer', 'Dairy Products', 340.00, 70), ('Khoya (Premium)', 'Dairy Products', 400.00, 40),
        ('Lassi (Sweet)', 'Dairy Products', 50.00, 130), ('Milk Powder', 'Dairy Products', 250.00, 90),
    ],
    'Patil Pav Center': [
        ('Instant Noodles', 'Packaged Foods', 45.00, 200), ('Pasta', 'Packaged Foods', 80.00, 150),
        ('Breakfast Cereal', 'Packaged Foods', 150.00, 100), ('Instant Soup Mix', 'Packaged Foods', 70.00, 120),
        ('Ready Pizza Base', 'Packaged Foods', 60.00, 80), ('Chocolate Spread', 'Packaged Foods', 200.00, 90),
        ('Peanut Butter', 'Packaged Foods', 180.00, 110), ('Biscuits', 'Packaged Foods', 30.00, 300),
        ('Cookies', 'Packaged Foods', 90.00, 150), ('Cake Mix', 'Packaged Foods', 140.00, 70),
    ],
    'Reddy ReadyServe': [
        ('Veg Pulao (Precooked)', 'Packaged Foods', 130.00, 100), ('Dal Tadka (Precooked)', 'Packaged Foods', 110.00, 120),
        ('Paneer Butter Masala (Precooked)', 'Packaged Foods', 160.00, 80), ('Veg Biryani (Precooked)', 'Packaged Foods', 140.00, 90),
        ('Matar Paneer (Precooked)', 'Packaged Foods', 150.00, 85), ('Rajma Masala (Precooked)', 'Packaged Foods', 120.00, 110),
        ('Kadhai Paneer (Precooked)', 'Packaged Foods', 170.00, 75), ('Pav Bhaji (Precooked)', 'Packaged Foods', 130.00, 95),
        ('Veg Korma (Precooked)', 'Packaged Foods', 150.00, 80), ('Chana Masala (Precooked)', 'Packaged Foods', 125.00, 100),
    ],
    'Khan Sauces & Oils': [
        ('Olive Oil', 'Packaged Foods', 320.00, 60), ('Mustard Oil', 'Packaged Foods', 250.00, 80),
        ('Sunflower Oil', 'Packaged Foods', 240.00, 90), ('Coconut Oil', 'Packaged Foods', 280.00, 70),
        ('Vinegar', 'Packaged Foods', 60.00, 150), ('Mayonnaise', 'Packaged Foods', 150.00, 100),
        ('Pizza Sauce', 'Packaged Foods', 120.00, 110), ('Red Chilli Sauce', 'Packaged Foods', 90.00, 130),
        ('Barbecue Sauce', 'Packaged Foods', 140.00, 80), ('Salad Dressing', 'Packaged Foods', 180.00, 70),
    ],
    'Yadav Snacks Mart': [
        ('Chips', 'Snacks & Beverages', 30.00, 300), ('Popcorn', 'Snacks & Beverages', 40.00, 250),
        ('Energy Drink', 'Snacks & Beverages', 90.00, 150), ('Green Tea', 'Snacks & Beverages', 180.00, 100),
        ('Fruit Juice', 'Snacks & Beverages', 120.00, 180), ('Iced Tea', 'Snacks & Beverages', 140.00, 120),
        ('Soft Drink', 'Snacks & Beverages', 35.00, 400), ('Salted Peanuts', 'Snacks & Beverages', 60.00, 200),
        ('Protein Bar', 'Snacks & Beverages', 90.00, 130), ('Coconut Water', 'Snacks & Beverages', 50.00, 220),
    ],
    'Joshi Beverage Supplies': [
        ('Instant Coffee Sachets', 'Snacks & Beverages', 150.00, 180), ('Herbal Tea', 'Snacks & Beverages', 200.00, 90),
        ('Black Tea', 'Snacks & Beverages', 180.00, 110), ('Cold Coffee Bottle', 'Snacks & Beverages', 80.00, 150),
        ('Energy Shots', 'Snacks & Beverages', 90.00, 120), ('Malt Drink Powder', 'Snacks & Beverages', 250.00, 80),
        ('Lemon Iced Tea', 'Snacks & Beverages', 140.00, 130), ('Brown Sugar', 'Grains & Cereals', 85.00, 100),
        ('Rock Salt', 'Grains & Cereals', 60.00, 140), ('Jaggery', 'Grains & Cereals', 70.00, 160),
    ],
    'Sinha Packaging House': [
        ('Plastic Containers', 'Other', 60.00, 500), ('Aluminium Foil Roll', 'Other', 120.00, 300),
        ('Wooden Spoons', 'Other', 30.00, 1000), ('Ice Cream Cups', 'Other', 25.00, 800),
        ('Food Storage Bags', 'Other', 50.00, 600), ('Baking Paper', 'Other', 80.00, 400),
        ('Measuring Cups', 'Other', 90.00, 200), ('Straws', 'Other', 15.00, 2000),
        ('Disposable Cups', 'Other', 20.00, 1500), ('Kitchen Towels', 'Other', 55.00, 250),
    ],
    'Mehta Sweet Essentials': [
        ('Rabdi Mix', 'Dairy Products', 150.00, 80), ('Gulab Jamun Mix', 'Dairy Products', 180.00, 100),
        ('Rasgulla Tin', 'Dairy Products', 220.00, 70), ('Kaju Katli Pack', 'Dairy Products', 350.00, 50),
        ('Peda', 'Dairy Products', 200.00, 90), ('Barfi', 'Dairy Products', 240.00, 85),
        ('Jalebi Mix', 'Dairy Products', 130.00, 110), ('Rose Syrup', 'Other', 90.00, 120),
        ('Saffron Strands', 'Other', 550.00, 30), ('Pistachio Kernels', 'Other', 800.00, 40),
    ],
    'Verma Green Cart': [
        ('Kale', 'Vegetables', 120.00, 90), ('Romaine Lettuce', 'Vegetables', 90.00, 110),
        ('Iceberg Lettuce', 'Vegetables', 95.00, 100), ('Parsley', 'Vegetables', 70.00, 130),
        ('Dill Leaves', 'Vegetables', 65.00, 140), ('Baby Spinach', 'Vegetables', 110.00, 120),
        ('Sweet Potato', 'Vegetables', 60.00, 180), ('Green Beans', 'Vegetables', 55.00, 200),
        ('Cluster Beans', 'Vegetables', 50.00, 220), ('Amaranth Leaves', 'Vegetables', 45.00, 250),
    ],
    'Dixit Base & Ready Foods': [
        ('Ready Dosa Batter', 'Packaged Foods', 90.00, 150), ('Idli Batter', 'Packaged Foods', 85.00, 160),
        ('Frozen Paratha', 'Packaged Foods', 120.00, 100), ('Ready Chapati', 'Packaged Foods', 60.00, 200),
        ('Pizza Dough', 'Packaged Foods', 100.00, 80), ('Ready Pasta Sauce', 'Packaged Foods', 150.00, 90),
        ('Instant Uttapam Mix', 'Packaged Foods', 140.00, 70), ('Veg Hakka Noodles (Precooked)', 'Packaged Foods', 110.00, 110),
        ('Schezwan Fried Rice (Precooked)', 'Packaged Foods', 130.00, 100), ('Manchurian Gravy (Precooked)', 'Packaged Foods', 150.00, 80),
    ],
}

# Insert products for each wholesaler
for wholesaler_id, wholesaler_name in wholesaler_info:
    if wholesaler_name in wholesaler_products:
        products = wholesaler_products[wholesaler_name]
        for product_name, category, price, stock in products:
            if stock == 0:
                status = 'Out of Stock'
            elif stock < 50:
                status = 'Low Stock'
            else:
                status = 'In Stock'
            
            views = random.randint(50, 500)
            likes = random.randint(5, 50)
            
            # Using INSERT OR IGNORE to prevent duplicates if script were to be modified
            cursor.execute('''
                INSERT INTO products (wholesaler_id, name, category, price, stock, group_buy_eligible, views, likes, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (wholesaler_id, product_name, category, price, stock, 1, views, likes, status))

# Generate realistic orders across all wholesalers
cursor.execute('SELECT id FROM products')
all_product_ids = [row[0] for row in cursor.fetchall()]

cursor.execute('SELECT id FROM wholesalers')
all_wholesaler_ids = [row[0] for row in cursor.fetchall()]

order_statuses = ['pending', 'processing', 'completed', 'completed', 'completed']
orders_data = []

for _ in range(200):
    vendor_id = random.randint(1, 15)
    product_id = random.choice(all_product_ids)
    
    cursor.execute('SELECT wholesaler_id, price FROM products WHERE id = ?', (product_id,))
    product_info = cursor.fetchone()
    wholesaler_id = product_info[0]
    price = product_info[1]
    
    quantity = random.randint(5, 100)
    total_amount = quantity * price
    status = random.choice(order_statuses)
    
    days_ago = random.randint(0, 60)
    order_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
    
    orders_data.append((wholesaler_id, vendor_id, product_id, quantity, total_amount, status, order_date))

cursor.executemany('INSERT INTO orders (wholesaler_id, vendor_id, product_id, quantity, total_amount, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)', orders_data)

# Generate reviews for different wholesalers
review_comments = [
    "Excellent quality products, always fresh and delivered on time!", "Good supplier with competitive prices and reliable service.",
    "Outstanding quality! Best wholesaler in the area.", "Products are good but delivery could be faster.",
    "Amazing variety and freshness. Highly recommended!", "Reliable supplier with consistent quality.",
    "Perfect for our business needs. Great customer service.", "Good experience overall. Fair pricing.",
    "Fresh products always available when needed.", "Professional service and quality products.",
    "Best prices in the market with good quality.", "Quick response and helpful staff.",
]

replies = [
    "Thank you for your feedback! We appreciate your business.", "We're working on improving our delivery times.",
    "Thanks for choosing us! We value your trust.", "We're glad to serve your business needs.",
    "Your satisfaction is our priority. Thank you!", None, None, None,
]

reviews_data = []
for wholesaler_id in all_wholesaler_ids:
    num_reviews = random.randint(3, 8)
    for _ in range(num_reviews):
        vendor_id = random.randint(1, 15)
        rating = random.randint(3, 5)
        comment = random.choice(review_comments)
        reply = random.choice(replies)
        reviews_data.append((wholesaler_id, vendor_id, rating, comment, reply))

cursor.executemany('INSERT INTO reviews (wholesaler_id, vendor_id, rating, comment, reply) VALUES (?, ?, ?, ?, ?)', reviews_data)

# Generate analytics data for all wholesalers
today = datetime.now()
analytics_data = []

for wholesaler_id in all_wholesaler_ids:
    for i in range(30):
        date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        base_orders = random.randint(8, 25)
        daily_orders = base_orders + random.randint(-5, 10)
        daily_revenue = daily_orders * random.uniform(600, 1500)
        daily_customers = random.randint(3, 12)
        analytics_data.append((wholesaler_id, date, daily_orders, daily_revenue, daily_customers))

cursor.executemany('INSERT INTO analytics (wholesaler_id, date, total_orders, total_revenue, active_customers) VALUES (?, ?, ?, ?, ?)', analytics_data)

# Insert sample payment methods
print("Inserting sample payment methods...")
import json

payment_methods_data = [
    # Vendor 1 (Raj Patel)
    (1, 'upi', json.dumps({'upi_id': 'rajpatel@okbank'}), True),
    (1, 'card', json.dumps({'card_number': '4589', 'card_brand': 'visa', 'card_holder': 'Raj K Patel', 'expiry': '12/28'}), False),
    # Vendor 2 (Priya Shah)
    (2, 'upi', json.dumps({'upi_id': 'priya91@ybl'}), True),
    # Vendor 3 (Amit Kumar)
    (3, 'card', json.dumps({'card_number': '5522', 'card_brand': 'mastercard', 'card_holder': 'Amit Kumar', 'expiry': '06/27'}), True),
]
cursor.executemany('INSERT INTO vendor_payment_methods (vendor_id, method_type, details, is_default) VALUES (?, ?, ?, ?)', payment_methods_data)

conn.commit()
conn.close()

print("✅ Comprehensive database created successfully!")
print("✅ All 13 wholesalers added with their specific products")
print("\n🚀 Run 'python app.py' to start Sahaayak with comprehensive data!")
