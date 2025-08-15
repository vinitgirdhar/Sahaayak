import sqlite3

# Connect to database
conn = sqlite3.connect('vendor_clubs.db')
cursor = conn.cursor()

# First, ensure we have a wholesaler
cursor.execute('SELECT id FROM wholesalers WHERE is_approved = 1 LIMIT 1')
wholesaler = cursor.fetchone()

if not wholesaler:
    # Create a sample wholesaler
    cursor.execute('''
        INSERT INTO wholesalers (name, phone, password, shop_name, sourcing_info, location, is_approved, trust_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('Fresh Farms Wholesale', '9876543210', 'password123', 'Fresh Farms Store', 
          'Direct from farmers', 'Mumbai', True, 4.8))
    wholesaler_id = cursor.lastrowid
else:
    wholesaler_id = wholesaler[0]

# Sample products for each category
sample_products = [
    # Vegetables (Produce category)
    ('Tomatoes', 'Produce', 'Fresh red tomatoes', 40, 'kg', 100, 'uploads/groceries.jpg'),
    ('Onions', 'Produce', 'Quality onions', 35, 'kg', 150, None),
    ('Potatoes', 'Produce', 'Fresh potatoes', 30, 'kg', 200, None),
    ('Green Chillies', 'Produce', 'Spicy green chillies', 80, 'kg', 50, None),
    ('Carrots', 'Produce', 'Orange carrots', 45, 'kg', 80, None),
    ('Cabbage', 'Produce', 'Fresh cabbage', 25, 'kg', 60, None),
    
    # Dairy
    ('Milk', 'Dairy & Alternatives', 'Fresh cow milk', 60, 'liter', 100, None),
    ('Paneer', 'Dairy & Alternatives', 'Fresh paneer', 280, 'kg', 50, None),
    ('Butter', 'Dairy & Alternatives', 'Amul butter', 450, 'kg', 30, None),
    ('Cheese', 'Dairy & Alternatives', 'Processed cheese', 380, 'kg', 25, None),
    
    # Dry Ingredients & Spices
    ('Turmeric Powder', 'Pantry Staples', 'Pure turmeric', 180, 'kg', 40, None),
    ('Red Chilli Powder', 'Pantry Staples', 'Spicy chilli powder', 200, 'kg', 35, None),
    ('Salt', 'Pantry Staples', 'Iodized salt', 20, 'kg', 100, None),
    ('Cumin Seeds', 'Pantry Staples', 'Whole cumin', 350, 'kg', 25, None),
    
    # Bakery
    ('White Bread', 'Bakery & Base Items', 'Fresh bread', 35, 'loaf', 50, None),
    ('Wheat Flour', 'Bakery & Base Items', 'Chakki atta', 45, 'kg', 100, None),
    ('Maida', 'Bakery & Base Items', 'All purpose flour', 40, 'kg', 80, None),
    
    # Oils & Sauces
    ('Cooking Oil', 'Sauces & Pastes', 'Refined oil', 150, 'liter', 60, None),
    ('Tomato Ketchup', 'Sauces & Pastes', 'Tomato sauce', 120, 'kg', 40, None),
    ('Soy Sauce', 'Sauces & Pastes', 'Dark soy sauce', 180, 'liter', 30, None),
]

# Insert products
for product in sample_products:
    cursor.execute('''
        INSERT OR IGNORE INTO products (wholesaler_id, name, category, description, price, unit, stock, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (wholesaler_id, *product))

conn.commit()

# Verify insertion
cursor.execute('SELECT COUNT(*) FROM products')
count = cursor.fetchone()[0]
print(f"✅ Total products in database: {count}")

# Show products by category
cursor.execute('''
    SELECT category, COUNT(*) as count 
    FROM products 
    GROUP BY category
''')
categories = cursor.fetchall()

print("\n📦 Products by category:")
for cat, count in categories:
    print(f"  - {cat}: {count} products")

conn.close()
print("\n✨ Sample products added successfully!")
