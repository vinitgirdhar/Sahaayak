"""
Seed database with comprehensive product catalog for all categories.
Products are linked to existing wholesaler(s).
"""
import sqlite3
from datetime import datetime
import random

DATABASE_NAME = 'vendor_clubs.db'

# Products organized by the category names used in routes.py category_mapping
PRODUCTS_BY_CATEGORY = {
    'Vegetables': [
        ('Organic Tomatoes', 45.0, 500),
        ('Fresh Spinach', 25.0, 300),
        ('Premium Carrots', 35.0, 400),
        ('Red Onions', 30.0, 600),
        ('Green Capsicum', 55.0, 250),
        ('Fresh Broccoli', 80.0, 150),
        ('Cauliflower', 40.0, 350),
        ('Green Beans', 60.0, 200),
        ('Cabbage', 25.0, 400),
        ('Cucumber', 30.0, 500),
        ('Lady Finger (Okra)', 45.0, 300),
        ('Bitter Gourd', 50.0, 200),
        ('Bottle Gourd', 35.0, 250),
        ('Pumpkin', 40.0, 180),
        ('Radish', 25.0, 350),
    ],
    'Dry Ingredients': [
        ('Toor Dal', 120.0, 300),
        ('Chana Dal', 95.0, 400),
        ('Moong Dal', 110.0, 350),
        ('Urad Dal', 130.0, 280),
        ('Masoor Dal', 100.0, 320),
        ('Rajma (Kidney Beans)', 140.0, 200),
        ('Kabuli Chana', 150.0, 250),
        ('Poha (Flattened Rice)', 55.0, 400),
        ('Suji (Semolina)', 45.0, 350),
        ('Besan (Gram Flour)', 70.0, 300),
        ('Maida (All Purpose Flour)', 40.0, 500),
        ('Atta (Whole Wheat)', 50.0, 600),
        ('Rice Flour', 55.0, 280),
        ('Corn Flour', 65.0, 250),
        ('Sabudana', 80.0, 200),
    ],
    'Dairy Products': [
        ('Fresh Milk (1L)', 60.0, 500),
        ('Paneer (200g)', 90.0, 300),
        ('Curd/Yogurt (400g)', 45.0, 400),
        ('Butter (100g)', 55.0, 350),
        ('Cheese Slices (200g)', 120.0, 200),
        ('Cream (200ml)', 80.0, 250),
        ('Buttermilk (500ml)', 30.0, 400),
        ('Ghee (500g)', 350.0, 150),
        ('Mozzarella Cheese', 180.0, 180),
        ('Condensed Milk', 95.0, 220),
        ('Skimmed Milk (1L)', 55.0, 300),
        ('Flavored Yogurt', 40.0, 350),
    ],
    'Bread & Bakery': [
        ('White Bread', 40.0, 400),
        ('Brown Bread', 50.0, 350),
        ('Pav (Dinner Rolls) 6pc', 30.0, 500),
        ('Burger Buns 4pc', 45.0, 300),
        ('Hot Dog Buns 4pc', 45.0, 280),
        ('Croissant 2pc', 80.0, 150),
        ('Rusk Pack', 55.0, 400),
        ('Naan (5pc)', 60.0, 350),
        ('Roti (10pc)', 50.0, 400),
        ('Paratha (5pc)', 70.0, 300),
        ('Pizza Base (2pc)', 90.0, 200),
        ('Garlic Bread', 85.0, 180),
    ],
    'Ready-to-Eat': [
        ('Frozen Samosa (10pc)', 120.0, 250),
        ('Frozen Paratha (5pc)', 95.0, 300),
        ('Instant Noodles Pack', 25.0, 600),
        ('Ready Mix Idli', 65.0, 350),
        ('Ready Mix Dosa', 70.0, 320),
        ('Canned Rajma Masala', 85.0, 200),
        ('Canned Chole', 80.0, 220),
        ('Frozen Veg Momos (10pc)', 130.0, 180),
        ('Instant Poha Mix', 55.0, 400),
        ('Ready Mix Upma', 60.0, 380),
        ('Frozen Spring Rolls (8pc)', 140.0, 150),
        ('Instant Soup Pack', 45.0, 500),
    ],
    'Oils & Condiments': [
        ('Sunflower Oil (1L)', 150.0, 400),
        ('Mustard Oil (1L)', 180.0, 350),
        ('Groundnut Oil (1L)', 200.0, 300),
        ('Olive Oil (500ml)', 450.0, 150),
        ('Coconut Oil (500ml)', 180.0, 280),
        ('Sesame Oil (200ml)', 120.0, 250),
        ('Tomato Ketchup (500g)', 95.0, 400),
        ('Mayonnaise (250g)', 110.0, 300),
        ('Soy Sauce (200ml)', 70.0, 350),
        ('Vinegar (500ml)', 45.0, 400),
        ('Green Chutney', 55.0, 280),
        ('Tamarind Paste', 65.0, 250),
    ],
    'Snacks & Beverages': [
        ('Chips (Large Pack)', 50.0, 500),
        ('Namkeen Mix (500g)', 120.0, 350),
        ('Biscuits Variety Pack', 80.0, 400),
        ('Roasted Peanuts (250g)', 60.0, 300),
        ('Makhana (Fox Nuts)', 150.0, 200),
        ('Dry Fruit Mix (250g)', 350.0, 150),
        ('Tea (250g)', 180.0, 400),
        ('Coffee (200g)', 250.0, 300),
        ('Green Tea (25 bags)', 150.0, 280),
        ('Soft Drink (2L)', 90.0, 350),
        ('Mango Juice (1L)', 110.0, 320),
        ('Coconut Water (1L)', 80.0, 280),
        ('Energy Drink', 120.0, 200),
        ('Lassi (500ml)', 50.0, 350),
    ],
    'Spices & Condiments': [
        ('Turmeric Powder (100g)', 40.0, 400),
        ('Red Chilli Powder (100g)', 55.0, 380),
        ('Coriander Powder (100g)', 45.0, 350),
        ('Cumin Seeds (100g)', 70.0, 300),
        ('Garam Masala (100g)', 85.0, 280),
        ('Biryani Masala (50g)', 60.0, 320),
        ('Pav Bhaji Masala (50g)', 45.0, 350),
        ('Chaat Masala (100g)', 50.0, 300),
        ('Black Pepper (50g)', 90.0, 250),
        ('Cinnamon Sticks (50g)', 80.0, 280),
        ('Cardamom (25g)', 120.0, 200),
        ('Cloves (25g)', 100.0, 220),
        ('Bay Leaves (20g)', 35.0, 400),
        ('Mustard Seeds (100g)', 40.0, 350),
        ('Fenugreek Seeds (100g)', 45.0, 320),
    ],
    'Spreads & Pantry': [
        ('Peanut Butter (250g)', 180.0, 250),
        ('Jam Mixed Fruit (250g)', 120.0, 300),
        ('Honey (250g)', 200.0, 200),
        ('Nutella (350g)', 380.0, 150),
        ('Cheese Spread (200g)', 140.0, 280),
        ('Pickle (Mango) 500g', 95.0, 350),
        ('Pickle (Mixed) 500g', 100.0, 320),
        ('Chyawanprash (500g)', 250.0, 180),
        ('Maple Syrup (250ml)', 350.0, 120),
        ('Tahini (200g)', 220.0, 150),
    ],
    'Grains & Cereals': [
        ('Basmati Rice (1kg)', 120.0, 500),
        ('Sona Masoori Rice (1kg)', 80.0, 450),
        ('Brown Rice (1kg)', 110.0, 300),
        ('Wheat (1kg)', 45.0, 600),
        ('Jowar (Sorghum) 500g', 55.0, 350),
        ('Bajra (Pearl Millet) 500g', 50.0, 380),
        ('Ragi (Finger Millet) 500g', 60.0, 320),
        ('Oats (500g)', 130.0, 280),
        ('Muesli (400g)', 250.0, 200),
        ('Corn Flakes (500g)', 180.0, 350),
        ('Quinoa (250g)', 280.0, 150),
        ('Barley (500g)', 70.0, 250),
    ],
    'Other': [  # For desserts, packaging, seafood-meat
        ('Disposable Plates (50pc)', 120.0, 300),
        ('Disposable Cups (50pc)', 80.0, 350),
        ('Aluminum Foil Roll', 150.0, 250),
        ('Cling Wrap', 95.0, 280),
        ('Paper Napkins (100pc)', 60.0, 400),
        ('Ice Cream (500ml)', 180.0, 200),
        ('Gulab Jamun Mix', 85.0, 300),
        ('Jalebi Mix', 75.0, 280),
        ('Rasgulla (1kg tin)', 250.0, 180),
        ('Chicken Fresh (500g)', 220.0, 150),
        ('Fish Fresh (500g)', 280.0, 120),
        ('Prawns (250g)', 350.0, 100),
        ('Eggs (12pc)', 90.0, 400),
        ('Mutton (500g)', 450.0, 80),
    ],
}

def seed_products():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get existing wholesaler IDs
    cursor.execute('SELECT id FROM wholesalers WHERE is_approved = 1')
    wholesalers = cursor.fetchall()
    
    if not wholesalers:
        print("No approved wholesalers found. Creating a default one...")
        cursor.execute('''
            INSERT INTO wholesalers (name, phone, password, shop_name, sourcing_info, location, is_approved, trust_score, response_rate, delivery_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('Mumbai Fresh Mart', '9999999999', 'password123', 'Fresh Mart Wholesale', 'Quality products from local farms', 'Ghatkopar', 1, 4.7, 95.0, 92.0))
        conn.commit()
        cursor.execute('SELECT id FROM wholesalers WHERE is_approved = 1')
        wholesalers = cursor.fetchall()
    
    wholesaler_ids = [w[0] for w in wholesalers]
    
    # Clear existing products to avoid duplicates
    cursor.execute('DELETE FROM products')
    conn.commit()
    print("Cleared existing products.")
    
    # Insert new products
    total_added = 0
    for category, products in PRODUCTS_BY_CATEGORY.items():
        for name, price, stock in products:
            wholesaler_id = random.choice(wholesaler_ids)
            views = random.randint(50, 500)
            likes = random.randint(5, 50)
            status = 'In Stock' if stock > 10 else ('Low Stock' if stock > 0 else 'Out of Stock')
            
            cursor.execute('''
                INSERT INTO products (wholesaler_id, name, category, price, stock, group_buy_eligible, image_path, views, likes, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (wholesaler_id, name, category, price, stock, 1, None, views, likes, status))
            total_added += 1
        
        print(f"  Added {len(products)} products to '{category}'")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Successfully added {total_added} products across {len(PRODUCTS_BY_CATEGORY)} categories!")
    print("\nCategory summary:")
    
    # Verify
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT category, COUNT(*) FROM products GROUP BY category ORDER BY category')
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} products")
    conn.close()

if __name__ == '__main__':
    seed_products()
