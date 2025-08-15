#!/usr/bin/env python3
"""
Validation script to verify that all mock data is present in the database
"""

import sqlite3

# Define the expected mock data
EXPECTED_DATA = {
    "Mumbai Fresh Mart": [
        ("Broccoli", "Vegetables", 90.00),
        ("Cauliflower", "Vegetables", 45.00),
        ("Bottle Gourd (Lauki)", "Vegetables", 35.00),
        ("Brinjal (Baingan)", "Vegetables", 40.00),
        ("Sweet Corn", "Vegetables", 60.00),
        ("Lady Finger (Bhindi)", "Vegetables", 55.00),
        ("Zucchini", "Vegetables", 120.00),
        ("Drumstick (Moringa)", "Vegetables", 80.00),
        ("Capsicum (Green)", "Vegetables", 70.00),
        ("Pumpkin", "Vegetables", 50.00),
    ],
    "Gupta Fresh Veggies": [
        ("Baby Potatoes", "Vegetables", 45.00),
        ("Spring Onions", "Vegetables", 40.00),
        ("Red Capsicum", "Vegetables", 90.00),
        ("Yellow Capsicum", "Vegetables", 95.00),
        ("Cherry Tomatoes", "Vegetables", 140.00),
        ("Green Peas", "Vegetables", 120.00),
        ("Turnip", "Vegetables", 35.00),
        ("Radish", "Vegetables", 30.00),
        ("Snake Gourd", "Vegetables", 60.00),
        ("Ash Gourd", "Vegetables", 55.00),
    ],
    "Sharma Masala Bhandar": [
        ("Coriander Powder", "Spices & Condiments", 140.00),
        ("Black Pepper (Whole)", "Spices & Condiments", 550.00),
        ("Mustard Seeds", "Spices & Condiments", 90.00),
        ("Curry Leaves (Dried)", "Spices & Condiments", 80.00),
        ("Fennel Seeds (Saunf)", "Spices & Condiments", 160.00),
        ("Fenugreek Seeds (Methi)", "Spices & Condiments", 100.00),
        ("Ajwain (Carom Seeds)", "Spices & Condiments", 120.00),
        ("Cloves (Laung)", "Spices & Condiments", 600.00),
        ("Cardamom (Elaichi)", "Spices & Condiments", 800.00),
        ("Cinnamon Sticks", "Spices & Condiments", 500.00),
    ],
    "Desai Dairy Depot": [
        ("Fresh Cream", "Dairy Products", 120.00),
        ("Cheese Slices", "Dairy Products", 150.00),
        ("Mozzarella Cheese", "Dairy Products", 380.00),
        ("Ghee (Organic)", "Dairy Products", 520.00),
        ("Yogurt (Flavored)", "Dairy Products", 70.00),
        ("Buttermilk", "Dairy Products", 40.00),
        ("Malai Paneer", "Dairy Products", 340.00),
        ("Khoya (Premium)", "Dairy Products", 400.00),
        ("Lassi (Sweet)", "Dairy Products", 50.00),
        ("Milk Powder", "Dairy Products", 250.00),
    ],
    "Patil Pav Center": [
        ("Instant Noodles", "Packaged Foods", 45.00),
        ("Pasta", "Packaged Foods", 80.00),
        ("Breakfast Cereal", "Packaged Foods", 150.00),
        ("Instant Soup Mix", "Packaged Foods", 70.00),
        ("Ready Pizza Base", "Packaged Foods", 60.00),
        ("Chocolate Spread", "Packaged Foods", 200.00),
        ("Peanut Butter", "Packaged Foods", 180.00),
        ("Biscuits", "Packaged Foods", 30.00),
        ("Cookies", "Packaged Foods", 90.00),
        ("Cake Mix", "Packaged Foods", 140.00),
    ],
    "Reddy ReadyServe": [
        ("Veg Pulao (Precooked)", "Packaged Foods", 130.00),
        ("Dal Tadka (Precooked)", "Packaged Foods", 110.00),
        ("Paneer Butter Masala (Precooked)", "Packaged Foods", 160.00),
        ("Veg Biryani (Precooked)", "Packaged Foods", 140.00),
        ("Matar Paneer (Precooked)", "Packaged Foods", 150.00),
        ("Rajma Masala (Precooked)", "Packaged Foods", 120.00),
        ("Kadhai Paneer (Precooked)", "Packaged Foods", 170.00),
        ("Pav Bhaji (Precooked)", "Packaged Foods", 130.00),
        ("Veg Korma (Precooked)", "Packaged Foods", 150.00),
        ("Chana Masala (Precooked)", "Packaged Foods", 125.00),
    ],
    "Khan Sauces & Oils": [
        ("Olive Oil", "Packaged Foods", 320.00),
        ("Mustard Oil", "Packaged Foods", 250.00),
        ("Sunflower Oil", "Packaged Foods", 240.00),
        ("Coconut Oil", "Packaged Foods", 280.00),
        ("Vinegar", "Packaged Foods", 60.00),
        ("Mayonnaise", "Packaged Foods", 150.00),
        ("Pizza Sauce", "Packaged Foods", 120.00),
        ("Red Chilli Sauce", "Packaged Foods", 90.00),
        ("Barbecue Sauce", "Packaged Foods", 140.00),
        ("Salad Dressing", "Packaged Foods", 180.00),
    ],
    "Yadav Snacks Mart": [
        ("Chips", "Snacks & Beverages", 30.00),
        ("Popcorn", "Snacks & Beverages", 40.00),
        ("Energy Drink", "Snacks & Beverages", 90.00),
        ("Green Tea", "Snacks & Beverages", 180.00),
        ("Fruit Juice", "Snacks & Beverages", 120.00),
        ("Iced Tea", "Snacks & Beverages", 140.00),
        ("Soft Drink", "Snacks & Beverages", 35.00),
        ("Salted Peanuts", "Snacks & Beverages", 60.00),
        ("Protein Bar", "Snacks & Beverages", 90.00),
        ("Coconut Water", "Snacks & Beverages", 50.00),
    ],
    "Joshi Beverage Supplies": [
        ("Instant Coffee Sachets", "Snacks & Beverages", 150.00),
        ("Herbal Tea", "Snacks & Beverages", 200.00),
        ("Black Tea", "Snacks & Beverages", 180.00),
        ("Cold Coffee Bottle", "Snacks & Beverages", 80.00),
        ("Energy Shots", "Snacks & Beverages", 90.00),
        ("Malt Drink Powder", "Snacks & Beverages", 250.00),
        ("Lemon Iced Tea", "Snacks & Beverages", 140.00),
        ("Brown Sugar", "Grains & Cereals", 85.00),
        ("Rock Salt", "Grains & Cereals", 60.00),
        ("Jaggery", "Grains & Cereals", 70.00),
    ],
    "Sinha Packaging House": [
        ("Plastic Containers", "Other", 60.00),
        ("Aluminium Foil Roll", "Other", 120.00),
        ("Wooden Spoons", "Other", 30.00),
        ("Ice Cream Cups", "Other", 25.00),
        ("Food Storage Bags", "Other", 50.00),
        ("Baking Paper", "Other", 80.00),
        ("Measuring Cups", "Other", 90.00),
        ("Straws", "Other", 15.00),
        ("Disposable Cups", "Other", 20.00),
        ("Kitchen Towels", "Other", 55.00),
    ],
    "Mehta Sweet Essentials": [
        ("Rabdi Mix", "Dairy Products", 150.00),
        ("Gulab Jamun Mix", "Dairy Products", 180.00),
        ("Rasgulla Tin", "Dairy Products", 220.00),
        ("Kaju Katli Pack", "Dairy Products", 350.00),
        ("Peda", "Dairy Products", 200.00),
        ("Barfi", "Dairy Products", 240.00),
        ("Jalebi Mix", "Dairy Products", 130.00),
        ("Rose Syrup", "Other", 90.00),
        ("Saffron Strands", "Other", 550.00),
        ("Pistachio Kernels", "Other", 800.00),
    ],
    "Verma Green Cart": [
        ("Kale", "Vegetables", 120.00),
        ("Romaine Lettuce", "Vegetables", 90.00),
        ("Iceberg Lettuce", "Vegetables", 95.00),
        ("Parsley", "Vegetables", 70.00),
        ("Dill Leaves", "Vegetables", 65.00),
        ("Baby Spinach", "Vegetables", 110.00),
        ("Sweet Potato", "Vegetables", 60.00),
        ("Green Beans", "Vegetables", 55.00),
        ("Cluster Beans", "Vegetables", 50.00),
        ("Amaranth Leaves", "Vegetables", 45.00),
    ],
    "Dixit Base & Ready Foods": [
        ("Ready Dosa Batter", "Packaged Foods", 90.00),
        ("Idli Batter", "Packaged Foods", 85.00),
        ("Frozen Paratha", "Packaged Foods", 120.00),
        ("Ready Chapati", "Packaged Foods", 60.00),
        ("Pizza Dough", "Packaged Foods", 100.00),
        ("Ready Pasta Sauce", "Packaged Foods", 150.00),
        ("Instant Uttapam Mix", "Packaged Foods", 140.00),
        ("Veg Hakka Noodles (Precooked)", "Packaged Foods", 110.00),
        ("Schezwan Fried Rice (Precooked)", "Packaged Foods", 130.00),
        ("Manchurian Gravy (Precooked)", "Packaged Foods", 150.00),
    ],
}

def validate_database():
    """Validate that all expected data is present in the database"""
    
    conn = sqlite3.connect('vendor_clubs.db')
    cursor = conn.cursor()
    
    # Get all current data from database
    cursor.execute('''
        SELECT w.name, p.name, p.category, p.price 
        FROM products p 
        JOIN wholesalers w ON p.wholesaler_id = w.id 
        ORDER BY w.name, p.name
    ''')
    
    db_data = cursor.fetchall()
    conn.close()
    
    # Convert database data to same format as expected data
    db_dict = {}
    for row in db_data:
        wholesaler_name = row[0]
        product_name = row[1]
        category = row[2]
        price = float(row[3])
        
        if wholesaler_name not in db_dict:
            db_dict[wholesaler_name] = []
        
        db_dict[wholesaler_name].append((product_name, category, price))
    
    # Validation results
    all_present = True
    missing_items = []
    extra_items = []
    
    print("🔍 MOCK DATA VALIDATION REPORT")
    print("=" * 50)
    
    # Check if all expected data is present
    for wholesaler, expected_products in EXPECTED_DATA.items():
        print(f"\n📊 {wholesaler}:")
        
        if wholesaler not in db_dict:
            print(f"   ❌ Wholesaler not found in database!")
            all_present = False
            continue
            
        db_products = db_dict[wholesaler]
        
        for expected_product in expected_products:
            if expected_product in db_products:
                print(f"   ✅ {expected_product[0]} - ₹{expected_product[2]}")
            else:
                print(f"   ❌ MISSING: {expected_product[0]} - ₹{expected_product[2]}")
                missing_items.append(f"{wholesaler}: {expected_product[0]}")
                all_present = False
    
    # Check for extra items not in mock data
    print("\n🔍 CHECKING FOR EXTRA ITEMS...")
    for wholesaler, db_products in db_dict.items():
        if wholesaler in EXPECTED_DATA:
            expected_products = EXPECTED_DATA[wholesaler]
            for db_product in db_products:
                if db_product not in expected_products:
                    extra_items.append(f"{wholesaler}: {db_product[0]}")
    
    # Final results
    print("\n" + "=" * 50)
    print("📋 VALIDATION SUMMARY:")
    print("=" * 50)
    
    if all_present and len(missing_items) == 0:
        print("✅ SUCCESS: All mock data is present in the database!")
    else:
        print("❌ ISSUES FOUND:")
        if missing_items:
            print(f"   Missing items: {len(missing_items)}")
            for item in missing_items:
                print(f"     - {item}")
    
    if extra_items:
        print(f"\n📝 Extra items found (not in mock data): {len(extra_items)}")
        for item in extra_items[:10]:  # Show only first 10
            print(f"     - {item}")
        if len(extra_items) > 10:
            print(f"     ... and {len(extra_items) - 10} more")
    
    # Statistics
    total_expected = sum(len(products) for products in EXPECTED_DATA.values())
    total_in_db = sum(len(products) for products in db_dict.values())
    
    print(f"\n📊 STATISTICS:")
    print(f"   Expected wholesalers: {len(EXPECTED_DATA)}")
    print(f"   Wholesalers in DB: {len(db_dict)}")
    print(f"   Expected products: {total_expected}")
    print(f"   Products in DB: {total_in_db}")
    print(f"   Missing items: {len(missing_items)}")
    print(f"   Extra items: {len(extra_items)}")
    
    return all_present and len(missing_items) == 0

if __name__ == "__main__":
    validate_database()
