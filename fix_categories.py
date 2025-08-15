#!/usr/bin/env python3
"""
Fix category mappings for better organization
"""

import sqlite3

def reorganize_categories():
    """Reorganize product categories for better browsing experience"""
    
    conn = sqlite3.connect('vendor_clubs.db')
    cursor = conn.cursor()
    
    print("🔧 REORGANIZING PRODUCT CATEGORIES...")
    print("=" * 50)
    
    # Category reorganization mappings
    category_updates = [
        # Bread & Bakery Items
        {
            'new_category': 'Bread & Bakery',
            'products': [
                'Biscuits', 'Cake Mix', 'Cookies', 'Ready Pizza Base',
                'Frozen Paratha', 'Ready Chapati', 'Ready Dosa Batter',
                'Idli Batter', 'Pizza Dough', 'Instant Uttapam Mix'
            ]
        },
        
        # Dry Ingredients & Staples
        {
            'new_category': 'Dry Ingredients',
            'products': [
                'Brown Sugar', 'Rock Salt', 'Jaggery', 'Breakfast Cereal',
                'Instant Noodles', 'Pasta'
            ]
        },
        
        # Oils & Condiments (separate from packaged foods)
        {
            'new_category': 'Oils & Condiments',
            'products': [
                'Olive Oil', 'Mustard Oil', 'Sunflower Oil', 'Coconut Oil',
                'Vinegar', 'Mayonnaise', 'Pizza Sauce', 'Red Chilli Sauce',
                'Barbecue Sauce', 'Salad Dressing'
            ]
        },
        
        # Ready-to-Eat/Precooked (separate category)
        {
            'new_category': 'Ready-to-Eat',
            'products': [
                'Veg Pulao (Precooked)', 'Dal Tadka (Precooked)', 
                'Paneer Butter Masala (Precooked)', 'Veg Biryani (Precooked)',
                'Matar Paneer (Precooked)', 'Rajma Masala (Precooked)',
                'Kadhai Paneer (Precooked)', 'Pav Bhaji (Precooked)',
                'Veg Korma (Precooked)', 'Chana Masala (Precooked)',
                'Veg Hakka Noodles (Precooked)', 'Schezwan Fried Rice (Precooked)',
                'Manchurian Gravy (Precooked)'
            ]
        },
        
        # Spreads & Pantry Items
        {
            'new_category': 'Spreads & Pantry',
            'products': [
                'Chocolate Spread', 'Peanut Butter', 'Instant Soup Mix',
                'Ready Pasta Sauce'
            ]
        }
    ]
    
    # Apply the updates
    for update in category_updates:
        new_category = update['new_category']
        products = update['products']
        
        print(f"\n📦 Creating category: {new_category}")
        
        for product_name in products:
            # Update the product category
            cursor.execute('''
                UPDATE products 
                SET category = ? 
                WHERE name = ?
            ''', (new_category, product_name))
            
            if cursor.rowcount > 0:
                print(f"   ✅ {product_name} → {new_category}")
            else:
                print(f"   ⚠️  {product_name} not found")
    
    # Commit changes
    conn.commit()
    
    # Show updated category distribution
    print("\n" + "=" * 50)
    print("📊 UPDATED CATEGORY DISTRIBUTION:")
    print("=" * 50)
    
    cursor.execute('''
        SELECT category, COUNT(*) as count 
        FROM products 
        GROUP BY category 
        ORDER BY category
    ''')
    
    categories = cursor.fetchall()
    for cat in categories:
        print(f"{cat[0]}: {cat[1]} products")
    
    conn.close()
    
    print(f"\n✅ Category reorganization complete!")
    return True

def update_route_mapping():
    """Update the category mapping in routes.py"""
    
    print("\n🔧 UPDATING ROUTE MAPPING...")
    print("=" * 50)
    
    # The new mapping we need
    new_mapping = """
    category_mapping = {
        'vegetables': 'Vegetables',
        'dry-ingredients': 'Dry Ingredients', 
        'dairy': 'Dairy Products',
        'breads': 'Bread & Bakery',
        'prepared': 'Ready-to-Eat',
        'oils-sauces': 'Oils & Condiments',
        'snacks': 'Snacks & Beverages',
        'spices': 'Spices & Condiments',
        'spreads': 'Spreads & Pantry',
        'packaging': 'Other',
        'grains': 'Grains & Cereals'
    }"""
    
    new_display_names = """
    category_display_names = {
        'vegetables': 'Fresh Vegetables',
        'dry-ingredients': 'Dry Ingredients & Staples', 
        'dairy': 'Dairy Products',
        'breads': 'Bread & Bakery Items',
        'prepared': 'Ready-to-Eat Meals',
        'oils-sauces': 'Oils & Condiments',
        'snacks': 'Snacks & Beverages',
        'spices': 'Spices & Seasonings',
        'spreads': 'Spreads & Pantry Items',
        'packaging': 'Packaging & Others',
        'grains': 'Grains & Cereals'
    }"""
    
    print("✅ New category mapping prepared")
    print("⚠️  You'll need to manually update routes.py with the new mappings")
    print("\nReplace the category_mapping and category_display_names in vendor_category() function")
    
    return True

if __name__ == "__main__":
    reorganize_categories()
    update_route_mapping()
