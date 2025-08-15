import sqlite3

# Connect to database
conn = sqlite3.connect('vendor_clubs.db')
cursor = conn.cursor()

print("=== CHECKING PRODUCTS IN DATABASE ===\n")

# Check all products
cursor.execute('''
    SELECT p.*, w.name as wholesaler_name 
    FROM products p 
    JOIN wholesalers w ON p.wholesaler_id = w.id
    ORDER BY p.category, p.name
''')
products = cursor.fetchall()

print(f"Total products in database: {len(products)}\n")

# Group by category
categories = {}
for product in products:
    category = product[3]  # category is at index 3
    if category not in categories:
        categories[category] = []
    categories[category].append(product)

# Display products by category
for category, items in categories.items():
    print(f"\n{category} ({len(items)} products):")
    print("-" * 50)
    for item in items:
        print(f"  - {item[2]} (₹{item[4]}) - Stock: {item[6]} - Wholesaler: {item[-1]}")

# Check if there are any approved wholesalers
print("\n\n=== CHECKING WHOLESALERS ===")
cursor.execute('SELECT * FROM wholesalers WHERE is_approved = 1')
wholesalers = cursor.fetchall()
print(f"Approved wholesalers: {len(wholesalers)}")
for w in wholesalers:
    print(f"  - {w[1]} (ID: {w[0]}) - Location: {w[6]}")

# Check unique categories
print("\n\n=== UNIQUE CATEGORIES IN DATABASE ===")
cursor.execute('SELECT DISTINCT category FROM products')
unique_categories = cursor.fetchall()
for cat in unique_categories:
    print(f"  - {cat[0]}")

conn.close()
