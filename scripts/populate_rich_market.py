import sqlite3
import random
from datetime import datetime

DATABASE_NAME = 'vendor_clubs.db'

# Define 4 wholesalers
WHOLESALERS = [
    {
        'name': 'Mumbai Fresh Mart',
        'phone': '9999999999',
        'password': 'password123',
        'shop_name': 'Fresh Mart Wholesale',
        'sourcing_info': 'Directly from Nashik and Pune local farms',
        'location': 'Ghatkopar',
        'is_approved': True,
        'trust_score': 4.8,
        'response_rate': 98.0,
        'delivery_rate': 95.0,
        'profile_photo': None
    },
    {
        'name': 'Nashik Agri Farms Wholesale',
        'phone': '9888888888',
        'password': 'password123',
        'shop_name': 'Nashik Agri Hub',
        'sourcing_info': 'Cooperative farm collective from Nashik valley',
        'location': 'Dadar Mandi',
        'is_approved': True,
        'trust_score': 4.9,
        'response_rate': 96.0,
        'delivery_rate': 97.0,
        'profile_photo': None
    },
    {
        'name': 'Pune Organic Hub',
        'phone': '9777777777',
        'password': 'password123',
        'shop_name': 'Pune Organic Produce',
        'sourcing_info': 'Certified organic vegetables and premium grains',
        'location': 'APMC Vashi',
        'is_approved': True,
        'trust_score': 4.7,
        'response_rate': 92.0,
        'delivery_rate': 90.0,
        'profile_photo': None
    },
    {
        'name': 'Byculla Vegetable Depot',
        'phone': '9666666666',
        'password': 'password123',
        'shop_name': 'Byculla Sabzi Depot',
        'sourcing_info': 'Bulk distributors for local street vendors',
        'location': 'Byculla',
        'is_approved': True,
        'trust_score': 4.6,
        'response_rate': 94.0,
        'delivery_rate': 91.0,
        'profile_photo': None
    }
]

# Comprehensive list of products focusing heavily on vegetables with English/Hindi transliterations
PRODUCTS_BY_CATEGORY = {
    'Vegetables': [
        ('Potato (Aloo)', 22.0, 1000),
        ('Onion (Pyaz)', 28.0, 1200),
        ('Tomato (Tamatar)', 35.0, 800),
        ('Cabbage (Patta Gobi)', 25.0, 400),
        ('Cauliflower (Phool Gobi)', 45.0, 350),
        ('Garlic (Lahsun)', 140.0, 200),
        ('Ginger (Adrak)', 90.0, 300),
        ('Green Chillies (Hari Mirch)', 60.0, 250),
        ('Coriander (Dhaniya)', 40.0, 500),
        ('Mint (Pudina)', 30.0, 300),
        ('Lemon (Nimbu)', 80.0, 400),
        ('Lady Finger (Bhindi)', 48.0, 450),
        ('Brinjal (Baingan)', 36.0, 400),
        ('Capsicum (Shimla Mirch)', 70.0, 350),
        ('Carrot (Gajar)', 45.0, 500),
        ('Radish (Mooli)', 30.0, 400),
        ('Spinach (Palak)', 20.0, 600),
        ('Fenugreek (Methi)', 25.0, 500),
        ('Beetroot (Chukandar)', 40.0, 300),
        ('Sweet Potato (Shakarkand)', 50.0, 250),
        ('Pumpkin (Kaddu)', 32.0, 300),
        ('Bottle Gourd (Lauki)', 28.0, 400),
        ('Bitter Gourd (Karela)', 52.0, 280),
        ('Ridge Gourd (Turai)', 45.0, 300),
        ('Green Peas (Matar)', 75.0, 500),
        ('Cucumber (Kheera)', 24.0, 600),
        ('Spring Onion (Pyaz Patta)', 35.0, 200),
        ('Mushroom (Button)', 180.0, 150),
        ('Broccoli (Premium)', 120.0, 100),
        ('French Beans', 65.0, 300),
        ('Zucchini (Green)', 110.0, 120),
        ('Colocasia Root (Arbi)', 55.0, 200),
        ('Drumstick (Shevga)', 70.0, 250),
        ('Pointed Gourd (Parwal)', 65.0, 200),
        ('Raw Banana (Kacha Kela)', 30.0, 400)
    ],
    'Dry Ingredients': [
        ('Toor Dal', 122.0, 500),
        ('Chana Dal', 96.0, 600),
        ('Moong Dal', 112.0, 400),
        ('Urad Dal', 128.0, 400),
        ('Masoor Dal', 102.0, 450),
        ('Rajma (Kidney Beans)', 138.0, 300),
        ('Kabuli Chana (Chickpeas)', 145.0, 350),
        ('Poha (Flattened Rice)', 54.0, 600),
        ('Suji (Semolina)', 46.0, 500),
        ('Besan (Gram Flour)', 74.0, 600),
        ('Maida (All Purpose Flour)', 42.0, 800),
        ('Atta (Whole Wheat)', 48.0, 1000),
        ('Rice Flour', 52.0, 400),
        ('Corn Flour', 60.0, 300),
        ('Sabudana (Tapioca Pearls)', 84.0, 350)
    ],
    'Dairy Products': [
        ('Fresh Milk (1L)', 62.0, 600),
        ('Paneer (200g)', 92.0, 400),
        ('Curd/Yogurt (400g)', 46.0, 450),
        ('Butter (100g)', 56.0, 400),
        ('Cheese Slices (200g)', 124.0, 300),
        ('Cream (200ml)', 82.0, 300),
        ('Buttermilk (500ml)', 32.0, 500),
        ('Ghee (500g)', 360.0, 200),
        ('Mozzarella Cheese (200g)', 185.0, 250),
        ('Condensed Milk (400g)', 98.0, 200)
    ],
    'Bread & Bakery': [
        ('White Bread (Slab)', 38.0, 500),
        ('Brown Bread (Slab)', 48.0, 400),
        ('Pav (Dinner Rolls) 6pc', 28.0, 800),
        ('Burger Buns 4pc', 44.0, 400),
        ('Hot Dog Buns 4pc', 44.0, 300),
        ('Naan (5pc Pack)', 58.0, 400),
        ('Roti (10pc Pack)', 48.0, 600),
        ('Paratha (5pc Pack)', 68.0, 400),
        ('Pizza Base (2pc Pack)', 85.0, 300)
    ],
    'Ready-to-Eat': [
        ('Frozen Samosa (10pc)', 115.0, 300),
        ('Frozen Paratha (5pc)', 92.0, 400),
        ('Instant Noodles Pack', 24.0, 1000),
        ('Ready Mix Idli (500g)', 62.0, 450),
        ('Ready Mix Dosa (500g)', 68.0, 450),
        ('Canned Rajma Masala', 82.0, 300),
        ('Canned Chole (Chickpeas)', 78.0, 300),
        ('Frozen Veg Momos (10pc)', 125.0, 250),
        ('Instant Poha Mix (100g)', 50.0, 500)
    ],
    'Oils & Condiments': [
        ('Sunflower Oil (1L)', 145.0, 500),
        ('Mustard Oil (1L)', 175.0, 450),
        ('Groundnut Oil (1L)', 195.0, 400),
        ('Olive Oil (500ml)', 440.0, 200),
        ('Coconut Oil (500ml)', 175.0, 350),
        ('Tomato Ketchup (500g)', 92.0, 500),
        ('Mayonnaise (250g)', 108.0, 400),
        ('Soy Sauce (200ml)', 68.0, 400),
        ('Vinegar (500ml)', 42.0, 500)
    ],
    'Snacks & Beverages': [
        ('Chips (Large Pack)', 48.0, 600),
        ('Namkeen Mix (500g)', 115.0, 400),
        ('Biscuits Variety Pack', 78.0, 500),
        ('Roasted Peanuts (250g)', 58.0, 400),
        ('Tea (250g)', 175.0, 500),
        ('Coffee (200g)', 240.0, 400),
        ('Soft Drink (2L)', 85.0, 500),
        ('Mango Juice (1L)', 108.0, 400),
        ('Coconut Water (1L)', 76.0, 350)
    ],
    'Spices & Condiments': [
        ('Turmeric Powder (100g)', 38.0, 500),
        ('Red Chilli Powder (100g)', 52.0, 480),
        ('Coriander Powder (100g)', 42.0, 450),
        ('Cumin Seeds (100g)', 68.0, 400),
        ('Garam Masala (100g)', 82.0, 380),
        ('Biryani Masala (50g)', 58.0, 400),
        ('Pav Bhaji Masala (50g)', 42.0, 450),
        ('Chaat Masala (100g)', 48.0, 400),
        ('Black Pepper (50g)', 85.0, 300)
    ],
    'Spreads & Pantry': [
        ('Peanut Butter (250g)', 175.0, 300),
        ('Jam Mixed Fruit (250g)', 115.0, 400),
        ('Honey (250g)', 195.0, 300),
        ('Nutella (350g)', 370.0, 200),
        ('Cheese Spread (200g)', 135.0, 350),
        ('Pickle (Mango) 500g', 92.0, 450)
    ],
    'Grains & Cereals': [
        ('Basmati Rice (1kg)', 115.0, 600),
        ('Sona Masoori Rice (1kg)', 78.0, 550),
        ('Brown Rice (1kg)', 105.0, 400),
        ('Wheat (1kg)', 42.0, 800),
        ('Jowar (Sorghum) 500g', 52.0, 450),
        ('Bajra (Pearl Millet) 500g', 48.0, 480),
        ('Ragi (Finger Millet) 500g', 56.0, 420),
        ('Oats (500g)', 125.0, 380)
    ],
    'Packaging': [
        ('Disposable Plates (50pc)', 115.0, 400),
        ('Disposable Cups (50pc)', 76.0, 450),
        ('Aluminum Foil Roll', 145.0, 300)
    ],
    'Desserts': [
        ('Ice Cream (500ml)', 175.0, 250),
        ('Gulab Jamun Mix', 82.0, 400)
    ],
    'Seafood & Meat': [
        ('Chicken Fresh (500g)', 220.0, 150),
        ('Fish Fresh (500g)', 280.0, 120),
        ('Prawns (250g)', 250.0, 100),
        ('Mutton (500g)', 450.0, 80),
        ('Eggs (12pc)', 85.0, 500)
    ]
}

def seed_rich_market():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # 1. Clear existing wholesalers & products
    cursor.execute('DELETE FROM products')
    cursor.execute('DELETE FROM wholesalers')
    conn.commit()
    print("Cleared existing products and wholesalers.")
    
    # Reset auto-increment
    cursor.execute('UPDATE sqlite_sequence SET seq = 0 WHERE name IN ("products", "wholesalers")')
    conn.commit()
    
    # 2. Insert new wholesalers
    wholesaler_ids = []
    for w in WHOLESALERS:
        cursor.execute('''
            INSERT INTO wholesalers (name, phone, password, shop_name, sourcing_info, location, is_approved, trust_score, response_rate, delivery_rate, profile_photo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (w['name'], w['phone'], w['password'], w['shop_name'], w['sourcing_info'], w['location'], w['is_approved'], w['trust_score'], w['response_rate'], w['delivery_rate'], w['profile_photo']))
        wholesaler_ids.append(cursor.lastrowid)
    
    conn.commit()
    print(f"Added {len(wholesaler_ids)} approved wholesalers.")
    
    # 3. Populate products distributed across all wholesalers
    total_added = 0
    for category, products in PRODUCTS_BY_CATEGORY.items():
        for name, base_price, base_stock in products:
            # We add this product for 2 to 3 different wholesalers to simulate choice and search comparison!
            num_sellers = random.randint(2, 3)
            sellers = random.sample(wholesaler_ids, num_sellers)
            
            # Generate name-deduplicated image path
            safe_name = "".join(c if c.isalnum() else "_" for c in name.lower()).strip('_')
            while "__" in safe_name:
                safe_name = safe_name.replace("__", "_")
            image_path = f"uploads/products/{safe_name}.jpg"
            
            for seller_id in sellers:
                # Add slight variance to price and stock for different wholesalers
                price = round(base_price * random.uniform(0.9, 1.1), 2)
                stock = int(base_stock * random.uniform(0.8, 1.2))
                views = random.randint(20, 400)
                likes = random.randint(2, 40)
                status = 'In Stock' if stock > 10 else ('Low Stock' if stock > 0 else 'Out of Stock')
                
                cursor.execute('''
                    INSERT INTO products (wholesaler_id, name, category, price, stock, group_buy_eligible, image_path, views, likes, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (seller_id, name, category, price, stock, 1, image_path, views, likes, status))
                total_added += 1
        
        print(f"  Added products for '{category}'")
        
    conn.commit()
    conn.close()
    print(f"\n[SUCCESS] Successfully seeded {total_added} products in total across {len(wholesaler_ids)} wholesalers!")

if __name__ == '__main__':
    seed_rich_market()
