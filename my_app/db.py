import sqlite3
from datetime import datetime, timedelta
import os
import json
from flask import current_app, has_app_context

DEFAULT_DATABASE_NAME = 'vendor_clubs.db'
DEMO_VENDOR_PHONE = '9876543210'
DEMO_WHOLESALER_PHONE = '9999999999'

DEMO_VENDOR_PROFILE = {
    'name': 'Raj Patel',
    'email': 'raj@example.com',
    'phone': DEMO_VENDOR_PHONE,
    'password': 'vendor123',
    'alternate_contact': '9876500000',
    'shop_name': 'Raj Snacks Corner',
    'goods_type': 'Tea, snacks and breakfast',
    'working_hours': '06:30 AM - 03:30 PM',
    'street_area': 'MG Road Market',
    'photo_path': 'uploads/profile_1_8afd4a28-4357-4265-914a-f21ce21c7f79_WhatsApp_Image_2025-07-12_at_18.21.22_2ca4db45.jpg',
    'pincode': '400086',
    'city': 'Mumbai',
    'location': 'Ghatkopar',
    'credits': 250.0,
}

DEMO_WHOLESALER_PROFILE = {
    'name': 'Mumbai Fresh Mart',
    'phone': DEMO_WHOLESALER_PHONE,
    'password': 'password123',
    'shop_name': 'Fresh Mart Wholesale',
    'sourcing_info': (
        'Fresh produce, staples, beverages and pantry items sourced daily from '
        'trusted markets across Mumbai for street vendors and small kitchens.'
    ),
    'location': 'Ghatkopar',
    'is_approved': 1,
    'trust_score': 4.8,
    'response_rate': 97.0,
    'delivery_rate': 94.0,
    'profile_photo': 'uploads/vendor_c9aa3e26-b4a8-49f4-8cfa-89234a460807_logo.jpg',
}

DEMO_PRODUCTS = [
    ('Organic Tomatoes', 'Vegetables', 45.0, 220, 'uploads/products/product_6_organic_tomatoes.jpg', 534, 48),
    ('Fresh Spinach', 'Vegetables', 28.0, 90, 'uploads/products/product_7_fresh_spinach.jpg', 412, 31),
    ('Premium Carrots', 'Vegetables', 36.0, 0, 'uploads/products/product_8_premium_carrots.jpg', 275, 18),
    ('Red Onions', 'Vegetables', 32.0, 260, 'uploads/products/product_9_red_onions.jpg', 486, 44),
    ('Green Capsicum', 'Vegetables', 58.0, 95, 'uploads/products/product_10_green_capsicum.jpg', 298, 24),
    ('Fresh Broccoli', 'Vegetables', 82.0, 18, 'uploads/products/product_11_fresh_broccoli.jpg', 240, 16),
    ('Cauliflower', 'Vegetables', 44.0, 70, 'uploads/products/product_12_cauliflower.jpg', 215, 15),
    ('Cucumber', 'Vegetables', 30.0, 140, 'uploads/products/product_15_cucumber.jpg', 325, 20),
    ('Basmati Rice (1kg)', 'Grains & Cereals', 125.0, 180, 'uploads/products/product_123_basmati_rice__1kg_.jpg', 390, 29),
    ('Turmeric Powder (100g)', 'Spices & Condiments', 42.0, 160, 'uploads/products/product_98_turmeric_powder__100g_.jpg', 344, 22),
    ('Cumin Seeds (100g)', 'Spices & Condiments', 72.0, 130, 'uploads/products/product_101_cumin_seeds__100g_.jpg', 268, 17),
    ('Peanut Butter (250g)', 'Spreads & Pantry', 185.0, 75, 'uploads/products/product_113_peanut_butter__250g_.jpg', 301, 26),
    ('Tea (250g)', 'Snacks & Beverages', 180.0, 90, 'uploads/products/product_90_tea__250g_.jpg', 223, 14),
    ('Sunflower Oil (1L)', 'Oils & Condiments', 155.0, 60, 'uploads/products/product_72_sunflower_oil__1l_.jpg', 248, 19),
    ('Mango Juice (1L)', 'Snacks & Beverages', 112.0, 85, 'uploads/products/product_94_mango_juice__1l_.jpg', 201, 12),
]

DEMO_ORDER_PLANS = [
    ('9876543210', 'completed', 14, [('Organic Tomatoes', 8), ('Basmati Rice (1kg)', 4)]),
    ('9876543210', 'completed', 8, [('Turmeric Powder (100g)', 6), ('Cumin Seeds (100g)', 4)]),
    ('9876543210', 'processing', 3, [('Fresh Spinach', 10), ('Peanut Butter (250g)', 2)]),
    ('9876543210', 'pending', 1, [('Green Capsicum', 12), ('Cauliflower', 8)]),
    ('9876543211', 'completed', 9, [('Red Onions', 20), ('Cucumber', 12)]),
    ('9876543212', 'completed', 6, [('Basmati Rice (1kg)', 10), ('Organic Tomatoes', 15)]),
    ('9876543213', 'cancelled', 4, [('Fresh Broccoli', 5), ('Tea (250g)', 3)]),
    ('9876543214', 'processing', 2, [('Sunflower Oil (1L)', 6), ('Mango Juice (1L)', 10)]),
]

DEMO_REVIEWS = [
    ('9876543210', 5, 'Very reliable for daily stock-up. Fresh produce arrives early and helps us serve breakfast rush on time.', 'Thanks Raj! We keep the morning dispatch slots reserved for regular vendors.'),
    ('9876543211', 4, 'Good prices on vegetables and staples. Packaging has improved a lot over the last few weeks.', None),
    ('9876543212', 5, 'The rice and spices quality is consistently good. Makes repeat ordering easy for our kitchen.', 'Appreciate the trust. We are glad the staples are working well for your kitchen.'),
    ('9876543214', 4, 'Fast response on urgent restock requests and the order status updates are easy to follow.', None),
]

DEMO_PAYMENT_METHODS = [
    ('upi', {'upi_id': 'raj-snacks@okicici', 'holder_name': 'Raj Patel'}, 1),
    ('card', {'card_holder': 'Raj Patel', 'brand': 'Visa', 'last4': '4242', 'expiry': '12/28'}, 0),
]


class ConfiguredDatabasePath(os.PathLike):
    """Resolve the active database path from Flask config when available."""

    def __init__(self, default_path):
        self.default_path = default_path

    def __fspath__(self):
        if has_app_context():
            return current_app.config.get('DATABASE', self.default_path)
        return self.default_path

    def __str__(self):
        return self.__fspath__()


DATABASE_NAME = ConfiguredDatabasePath(DEFAULT_DATABASE_NAME)


def get_database_path():
    return os.fspath(DATABASE_NAME)


def get_connection(row_factory=None):
    conn = sqlite3.connect(get_database_path())
    if row_factory is not None:
        conn.row_factory = row_factory
    return conn


def _status_for_stock(stock):
    if stock > 50:
        return 'In Stock'
    if stock > 0:
        return 'Low Stock'
    return 'Out of Stock'


def _ensure_demo_vendor(cursor):
    cursor.execute('SELECT id FROM vendors WHERE phone = ?', (DEMO_VENDOR_PHONE,))
    row = cursor.fetchone()

    values = (
        DEMO_VENDOR_PROFILE['name'],
        DEMO_VENDOR_PROFILE['email'],
        DEMO_VENDOR_PROFILE['phone'],
        DEMO_VENDOR_PROFILE['password'],
        DEMO_VENDOR_PROFILE['alternate_contact'],
        DEMO_VENDOR_PROFILE['shop_name'],
        DEMO_VENDOR_PROFILE['goods_type'],
        DEMO_VENDOR_PROFILE['working_hours'],
        DEMO_VENDOR_PROFILE['street_area'],
        DEMO_VENDOR_PROFILE['photo_path'],
        DEMO_VENDOR_PROFILE['pincode'],
        DEMO_VENDOR_PROFILE['city'],
        DEMO_VENDOR_PROFILE['location'],
        1,
        DEMO_VENDOR_PROFILE['credits'],
    )

    if row:
        cursor.execute('''
            UPDATE vendors
            SET name = ?, email = ?, phone = ?, password = ?, alternate_contact = ?,
                shop_name = ?, goods_type = ?, working_hours = ?, street_area = ?,
                photo_path = ?, pincode = ?, city = ?, location = ?, is_approved = ?,
                credits = ?
            WHERE id = ?
        ''', values + (row[0],))
        return row[0]

    cursor.execute('''
        INSERT INTO vendors (
            name, email, phone, password, alternate_contact, shop_name, goods_type,
            working_hours, street_area, photo_path, pincode, city, location,
            is_approved, credits
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', values)
    return cursor.lastrowid


def _ensure_demo_wholesaler(cursor):
    cursor.execute('SELECT id FROM wholesalers WHERE phone = ?', (DEMO_WHOLESALER_PHONE,))
    row = cursor.fetchone()

    values = (
        DEMO_WHOLESALER_PROFILE['name'],
        DEMO_WHOLESALER_PROFILE['phone'],
        DEMO_WHOLESALER_PROFILE['password'],
        DEMO_WHOLESALER_PROFILE['shop_name'],
        DEMO_WHOLESALER_PROFILE['sourcing_info'],
        DEMO_WHOLESALER_PROFILE['location'],
        DEMO_WHOLESALER_PROFILE['is_approved'],
        DEMO_WHOLESALER_PROFILE['trust_score'],
        DEMO_WHOLESALER_PROFILE['response_rate'],
        DEMO_WHOLESALER_PROFILE['delivery_rate'],
        DEMO_WHOLESALER_PROFILE['profile_photo'],
    )

    if row:
        cursor.execute('''
            UPDATE wholesalers
            SET name = ?, phone = ?, password = ?, shop_name = ?, sourcing_info = ?,
                location = ?, is_approved = ?, trust_score = ?, response_rate = ?,
                delivery_rate = ?, profile_photo = ?
            WHERE id = ?
        ''', values + (row[0],))
        return row[0]

    cursor.execute('''
        INSERT INTO wholesalers (
            name, phone, password, shop_name, sourcing_info, location,
            is_approved, trust_score, response_rate, delivery_rate, profile_photo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', values)
    return cursor.lastrowid


def _ensure_demo_products(cursor, wholesaler_id):
    product_price_map = {}

    for name, category, price, stock, image_path, views, likes in DEMO_PRODUCTS:
        status = _status_for_stock(stock)
        cursor.execute('SELECT id FROM products WHERE wholesaler_id = ? AND name = ?', (wholesaler_id, name))
        row = cursor.fetchone()

        values = (
            category,
            price,
            stock,
            1,
            image_path,
            views,
            likes,
            status,
        )

        if row:
            cursor.execute('''
                UPDATE products
                SET category = ?, price = ?, stock = ?, group_buy_eligible = ?,
                    image_path = ?, views = ?, likes = ?, status = ?
                WHERE id = ?
            ''', values + (row[0],))
        else:
            cursor.execute('''
                INSERT INTO products (
                    wholesaler_id, name, category, price, stock, group_buy_eligible,
                    image_path, views, likes, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (wholesaler_id, name) + values)

        product_price_map[name] = price

    return product_price_map


def _ensure_demo_reviews(cursor, wholesaler_id):
    cursor.execute('SELECT id, phone FROM vendors')
    vendor_ids = {phone: vendor_id for vendor_id, phone in cursor.fetchall()}

    for phone, rating, comment, reply in DEMO_REVIEWS:
        vendor_id = vendor_ids.get(phone)
        if not vendor_id:
            continue

        cursor.execute('''
            SELECT id FROM reviews
            WHERE wholesaler_id = ? AND vendor_id = ? AND comment = ?
        ''', (wholesaler_id, vendor_id, comment))
        if cursor.fetchone():
            continue

        cursor.execute('''
            INSERT INTO reviews (wholesaler_id, vendor_id, rating, comment, reply)
            VALUES (?, ?, ?, ?, ?)
        ''', (wholesaler_id, vendor_id, rating, comment, reply))


def _ensure_demo_payment_methods(cursor, vendor_id):
    cursor.execute('SELECT COUNT(*) FROM vendor_payment_methods WHERE vendor_id = ?', (vendor_id,))
    if cursor.fetchone()[0] > 0:
        return

    for method_type, details, is_default in DEMO_PAYMENT_METHODS:
        cursor.execute('''
            INSERT INTO vendor_payment_methods (vendor_id, method_type, details, is_default)
            VALUES (?, ?, ?, ?)
        ''', (vendor_id, method_type, json.dumps(details), is_default))


def _ensure_demo_orders(cursor, wholesaler_id, product_price_map):
    cursor.execute('SELECT COUNT(*) FROM orders WHERE wholesaler_id = ?', (wholesaler_id,))
    if cursor.fetchone()[0] > 0:
        return

    cursor.execute('SELECT id, phone FROM vendors')
    vendor_ids = {phone: vendor_id for vendor_id, phone in cursor.fetchall()}

    for index, (phone, status, days_ago, items) in enumerate(DEMO_ORDER_PLANS):
        vendor_id = vendor_ids.get(phone)
        if not vendor_id:
            continue

        created_at = (datetime.now() - timedelta(days=days_ago, hours=index)).strftime('%Y-%m-%d %H:%M:%S')
        total_amount = sum(product_price_map[name] * quantity for name, quantity in items)

        cursor.execute('''
            INSERT INTO orders (wholesaler_id, vendor_id, total_amount, status, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (wholesaler_id, vendor_id, total_amount, status, created_at))
        order_id = cursor.lastrowid

        for name, quantity in items:
            cursor.execute('SELECT id, price FROM products WHERE wholesaler_id = ? AND name = ?', (wholesaler_id, name))
            product = cursor.fetchone()
            if not product:
                continue

            product_id, price = product
            line_total = price * quantity
            cursor.execute('''
                INSERT INTO order_items (order_id, product_id, quantity, price, total)
                VALUES (?, ?, ?, ?, ?)
            ''', (order_id, product_id, quantity, price, line_total))


def _ensure_demo_analytics(cursor, wholesaler_id):
    today = datetime.now()
    for offset in range(30):
        date_value = (today - timedelta(days=offset)).strftime('%Y-%m-%d')
        total_orders = 14 + ((offset * 3) % 7)
        total_revenue = float(total_orders * (820 + ((offset % 5) * 35)))
        active_customers = 5 + (offset % 4)

        cursor.execute('SELECT id FROM analytics WHERE wholesaler_id = ? AND date = ?', (wholesaler_id, date_value))
        row = cursor.fetchone()
        if row:
            cursor.execute('''
                UPDATE analytics
                SET total_orders = ?, total_revenue = ?, active_customers = ?
                WHERE id = ?
            ''', (total_orders, total_revenue, active_customers, row[0]))
        else:
            cursor.execute('''
                INSERT INTO analytics (wholesaler_id, date, total_orders, total_revenue, active_customers)
                VALUES (?, ?, ?, ?, ?)
            ''', (wholesaler_id, date_value, total_orders, total_revenue, active_customers))


def ensure_demo_showcase_data(cursor):
    vendor_id = _ensure_demo_vendor(cursor)
    wholesaler_id = _ensure_demo_wholesaler(cursor)
    product_price_map = _ensure_demo_products(cursor, wholesaler_id)
    _ensure_demo_reviews(cursor, wholesaler_id)
    _ensure_demo_payment_methods(cursor, vendor_id)
    _ensure_demo_orders(cursor, wholesaler_id, product_price_map)
    _ensure_demo_analytics(cursor, wholesaler_id)

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Vendors table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            password TEXT,
            alternate_contact TEXT,
            shop_name TEXT,
            goods_type TEXT,
            working_hours TEXT,
            street_area TEXT,
            photo_path TEXT,
            pincode TEXT,
            city TEXT,
            location TEXT,
            is_approved BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Wholesalers table
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
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            status TEXT DEFAULT 'In Stock',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (wholesaler_id) REFERENCES wholesalers (id)
        )
    ''')
    
    # Orders table - Updated for multi-item orders
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wholesaler_id INTEGER,
            vendor_id INTEGER,
            total_amount REAL,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (wholesaler_id) REFERENCES wholesalers (id),
            FOREIGN KEY (vendor_id) REFERENCES vendors (id)
        )
    ''')

    # Order items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            price REAL,
            total REAL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Reviews table with reply column
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
    
    # Donations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_id INTEGER,
            food_description TEXT NOT NULL,
            quantity TEXT NOT NULL,
            pickup_address TEXT NOT NULL,
            pickup_time TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vendor_id) REFERENCES vendors (id)
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
    
    # Check if reply column exists in reviews table, if not add it
    cursor.execute("PRAGMA table_info(reviews)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'reply' not in columns:
        cursor.execute('ALTER TABLE reviews ADD COLUMN reply TEXT')
    
    # Check and add profile_photo column to wholesalers
    cursor.execute("PRAGMA table_info(wholesalers)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'profile_photo' not in columns:
        cursor.execute('ALTER TABLE wholesalers ADD COLUMN profile_photo TEXT')
        print("✅ Added profile_photo column to wholesalers table")

    # Check and add new columns to vendors table
    cursor.execute("PRAGMA table_info(vendors)")
    columns = [column[1] for column in cursor.fetchall()]
    new_columns = {
        'alternate_contact': 'TEXT',
        'shop_name': 'TEXT',
        'goods_type': 'TEXT',
        'working_hours': 'TEXT',
        'street_area': 'TEXT',
        'photo_path': 'TEXT',
        'pincode': 'TEXT',
        'city': 'TEXT'
    }
    for col, col_type in new_columns.items():
        if col not in columns:
            cursor.execute(f'ALTER TABLE vendors ADD COLUMN {col} {col_type}')
            print(f"✅ Added {col} column to vendors table")

    # Check and add credits column to vendors
    cursor.execute("PRAGMA table_info(vendors)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'credits' not in columns:
        cursor.execute('ALTER TABLE vendors ADD COLUMN credits REAL DEFAULT 0.0')
        print("✅ Added credits column to vendors table")

    # Insert sample data if empty
    cursor.execute('SELECT COUNT(*) FROM vendors')
    if cursor.fetchone()[0] == 0:
        # Sample vendors
        vendors_data = [
            ('Raj Patel', 'raj@example.com', '9876543210', 'vendor123', 'Ghatkopar', 1),
            ('Priya Shah', 'priya@example.com', '9876543211', 'vendor123', 'Ghatkopar', 1),
            ('Amit Kumar', 'amit@example.com', '9876543212', 'vendor123', 'Ghatkopar', 1),
            ('Sunita Devi', 'sunita@example.com', '9876543213', 'vendor123', 'Andheri', 1),
            ('Ravi Singh', 'ravi@example.com', '9876543214', 'vendor123', 'Andheri', 1),
        ]
        cursor.executemany('INSERT INTO vendors (name, email, phone, password, location, is_approved) VALUES (?, ?, ?, ?, ?, ?)', vendors_data)
        
        # Sample wholesaler
        cursor.execute('''
            INSERT INTO wholesalers (name, phone, password, shop_name, sourcing_info, location, is_approved, trust_score, response_rate, delivery_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('Mumbai Fresh Mart', '9999999999', 'password123', 'Fresh Mart Wholesale', 'Quality products from local farms', 'Ghatkopar', 1, 4.7, 95.0, 92.0))
        
        wholesaler_id = cursor.lastrowid
        
        # Sample products
        products_data = [
            (wholesaler_id, 'Organic Tomatoes', 'Vegetables', 45.0, 500, 1, None, 234, 12, 'In Stock'),
            (wholesaler_id, 'Fresh Spinach', 'Vegetables', 25.0, 200, 1, None, 156, 8, 'Low Stock'),
            (wholesaler_id, 'Premium Carrots', 'Vegetables', 35.0, 0, 1, None, 89, 5, 'Out of Stock'),
            (wholesaler_id, 'Red Onions', 'Vegetables', 30.0, 300, 1, None, 312, 18, 'In Stock'),
            (wholesaler_id, 'Basmati Rice', 'Grains & Cereals', 85.0, 150, 1, None, 445, 25, 'In Stock'),
        ]
        cursor.executemany('INSERT INTO products (wholesaler_id, name, category, price, stock, group_buy_eligible, image_path, views, likes, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', products_data)
        
        # Sample reviews with replies
        reviews_data = [
            (wholesaler_id, 1, 5, 'Excellent quality vegetables, always fresh and delivered on time.', None),
            (wholesaler_id, 2, 4, 'Good products and reliable supplier. Competitive pricing.', 'Thank you for your feedback!'),
            (wholesaler_id, 3, 5, 'Outstanding service! Best wholesaler in the area.', None),
            (wholesaler_id, 4, 4, 'Quality products, but delivery could be faster.', 'We are working on improving delivery times.'),
        ]
        cursor.executemany('INSERT INTO reviews (wholesaler_id, vendor_id, rating, comment, reply) VALUES (?, ?, ?, ?, ?)', reviews_data)
        
        # Sample analytics data
        today = datetime.now()
        analytics_data = []
        for i in range(30):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            orders = 15 + (i % 10)
            revenue = float(orders * 850.0)
            customers = 8 + (i % 5)
            analytics_data.append((wholesaler_id, date, orders, revenue, customers))
        
        cursor.executemany('INSERT INTO analytics (wholesaler_id, date, total_orders, total_revenue, active_customers) VALUES (?, ?, ?, ?, ?)', analytics_data)

    ensure_demo_showcase_data(cursor)
    
    conn.commit()
    conn.close()

def get_dashboard_stats(wholesaler_id):
    """Fetches dashboard statistics for a given wholesaler."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get total products
    cursor.execute('SELECT COUNT(*) FROM products WHERE wholesaler_id = ?', (wholesaler_id,))
    total_products = cursor.fetchone()[0]
    
    # Get pending orders
    cursor.execute('SELECT COUNT(*) FROM orders WHERE wholesaler_id = ? AND status = "pending"', (wholesaler_id,))
    pending_orders = cursor.fetchone()[0]
    
    # Get this month's revenue from completed orders
    current_month = datetime.now().strftime('%Y-%m')
    cursor.execute('''
        SELECT COALESCE(SUM(total_amount), 0) FROM orders 
        WHERE wholesaler_id = ? AND created_at LIKE ? AND status = "completed"
    ''', (wholesaler_id, f'{current_month}%'))
    month_revenue = cursor.fetchone()[0] or 0
    
    # Get active customers (vendors who ordered this month)
    cursor.execute('''
        SELECT COUNT(DISTINCT vendor_id) FROM orders 
        WHERE wholesaler_id = ? AND created_at >= date('now', 'start of month')
    ''', (wholesaler_id,))
    active_customers = cursor.fetchone()[0]
    
    # Get wholesaler performance data
    cursor.execute('SELECT trust_score, response_rate, delivery_rate FROM wholesalers WHERE id = ?', (wholesaler_id,))
    performance = cursor.fetchone()
    
    conn.close()
    
    return {
        'total_products': total_products,
        'pending_orders': pending_orders,
        'month_revenue': float(month_revenue),
        'active_customers': active_customers,
        'trust_score': performance[0] if performance else 4.7,
        'response_rate': performance[1] if performance else 95.0,
        'delivery_rate': performance[2] if performance else 92.0
    }

