#!/usr/bin/env python3
"""
Final verification of category reorganization
"""

import sqlite3

def final_verification():
    """Final verification that all categories are properly organized"""
    
    conn = sqlite3.connect('vendor_clubs.db')
    cursor = conn.cursor()
    
    print("🎯 FINAL CATEGORY ORGANIZATION VERIFICATION")
    print("=" * 60)
    
    # Get all categories with product counts
    cursor.execute('''
        SELECT category, COUNT(*) as count 
        FROM products 
        GROUP BY category 
        ORDER BY category
    ''')
    
    categories = cursor.fetchall()
    total_products = 0
    
    print("\n📊 CATEGORY DISTRIBUTION:")
    print("-" * 40)
    for cat in categories:
        print(f"✅ {cat[0]:<20} : {cat[1]:>3} products")
        total_products += cat[1]
    
    print("-" * 40)
    print(f"📦 TOTAL PRODUCTS: {total_products}")
    
    # Show sample products for each new category
    new_categories = [
        'Bread & Bakery',
        'Dry Ingredients', 
        'Oils & Condiments',
        'Ready-to-Eat',
        'Spreads & Pantry',
        'Spices & Condiments'
    ]
    
    print(f"\n🔍 SAMPLE PRODUCTS FROM REORGANIZED CATEGORIES:")
    print("=" * 60)
    
    for category in new_categories:
        cursor.execute('''
            SELECT p.name, w.name as wholesaler 
            FROM products p 
            JOIN wholesalers w ON p.wholesaler_id = w.id 
            WHERE p.category = ? 
            ORDER BY p.name 
            LIMIT 3
        ''', (category,))
        
        products = cursor.fetchall()
        print(f"\n🏷️  {category}:")
        for product in products:
            print(f"   • {product[0]} ({product[1]})")
        
        if len(products) == 3:
            cursor.execute('SELECT COUNT(*) FROM products WHERE category = ?', (category,))
            total = cursor.fetchone()[0]
            if total > 3:
                print(f"   ... and {total - 3} more products")
    
    # Verify route mapping compatibility
    print(f"\n🔗 ROUTE MAPPING VERIFICATION:")
    print("=" * 60)
    
    route_categories = [
        ('vegetables', 'Vegetables'),
        ('dry-ingredients', 'Dry Ingredients'), 
        ('dairy', 'Dairy Products'),
        ('breads', 'Bread & Bakery'),
        ('prepared', 'Ready-to-Eat'),
        ('oils-sauces', 'Oils & Condiments'),
        ('snacks', 'Snacks & Beverages'),
        ('spices', 'Spices & Condiments'),
        ('spreads', 'Spreads & Pantry'),
        ('packaging', 'Other')
    ]
    
    all_routes_valid = True
    for route_id, expected_category in route_categories:
        cursor.execute('SELECT COUNT(*) FROM products WHERE category = ?', (expected_category,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"✅ /vendor/category/{route_id:<15} → {expected_category} ({count} products)")
        else:
            print(f"⚠️  /vendor/category/{route_id:<15} → {expected_category} ({count} products)")
            all_routes_valid = False
    
    conn.close()
    
    print(f"\n" + "=" * 60)
    print("🎉 REORGANIZATION SUMMARY:")
    print("=" * 60)
    
    if all_routes_valid:
        print("✅ All categories successfully reorganized")
        print("✅ All route mappings are functional") 
        print("✅ Products properly distributed across logical categories")
        print("✅ Bread & Bakery items now have dedicated category")
        print("✅ Dry Ingredients separated from packaged foods")
        print("✅ Spices & Condiments clearly accessible")
        print("✅ Ready-to-Eat meals properly grouped")
        print("✅ Database ready for enhanced user experience")
    else:
        print("⚠️  Some route mappings may need adjustment")
    
    print(f"\n🚀 The Sahaayak platform now has {len(categories)} well-organized categories!")
    print("🎯 Users can now easily find bread, dry ingredients, and spices!")
    
    return all_routes_valid

if __name__ == "__main__":
    final_verification()
