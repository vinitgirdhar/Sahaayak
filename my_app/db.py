import sqlite3
from datetime import datetime, timedelta
import os

# Note: In a larger app, you might pass the database path from the config.
DATABASE_NAME = 'vendor_clubs.db'

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    conn = sqlite3.connect(DATABASE_NAME)
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
    
    conn.commit()
    conn.close()

def get_dashboard_stats(wholesaler_id):
    """Fetches dashboard statistics for a given wholesaler."""
    conn = sqlite3.connect(DATABASE_NAME)
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

