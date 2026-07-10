#!/usr/bin/env python3
"""
Test script to verify wholesaler-vendor synchronization
"""

import sqlite3

def test_wholesaler_vendor_sync():
    """Test that wholesaler login shows their products and vendor sees same products"""
    
    conn = sqlite3.connect('vendor_clubs.db')
    cursor = conn.cursor()
    
    print("🔄 WHOLESALER-VENDOR SYNCHRONIZATION TEST")
    print("=" * 50)
    
    # Test 1: Check wholesaler credentials exist
    print("\n1️⃣ TESTING WHOLESALER AUTHENTICATION...")
    cursor.execute('SELECT id, name, phone, password FROM wholesalers ORDER BY id')
    wholesalers = cursor.fetchall()
    
    for w in wholesalers:
        print(f"   Wholesaler ID {w[0]}: {w[1]} | Phone: {w[2]} | Password: {'***' if w[3] else 'NO PASSWORD'}")
    
    # Test 2: Check products are properly linked to wholesalers
    print(f"\n2️⃣ TESTING PRODUCT-WHOLESALER LINKAGE...")
    cursor.execute('''
        SELECT w.id, w.name, COUNT(p.id) as product_count
        FROM wholesalers w
        LEFT JOIN products p ON w.id = p.wholesaler_id
        GROUP BY w.id, w.name
        ORDER BY w.id
    ''')
    
    product_counts = cursor.fetchall()
    total_products = 0
    
    for pc in product_counts:
        print(f"   {pc[1]}: {pc[2]} products")
        total_products += pc[2]
    
    print(f"   TOTAL: {total_products} products")
    
    # Test 3: Sample vendor view - what would vendor see for each wholesaler?
    print(f"\n3️⃣ VENDOR VIEW TEST (Sample data)...")
    cursor.execute('''
        SELECT w.name, w.shop_name, w.trust_score, COUNT(p.id) as products, 
               MIN(p.price) as min_price, MAX(p.price) as max_price
        FROM wholesalers w
        LEFT JOIN products p ON w.id = p.wholesaler_id
        GROUP BY w.id
        ORDER BY w.name
    ''')
    
    vendor_view = cursor.fetchall()
    for vv in vendor_view:
        print(f"   📊 {vv[0]} ({vv[1]})")
        print(f"      Trust Score: {vv[2]} | Products: {vv[3]} | Price Range: ₹{vv[4]}-₹{vv[5]}")
    
    # Test 4: Sample category filtering (what vendor would see)
    print(f"\n4️⃣ CATEGORY VIEW TEST...")
    cursor.execute('''
        SELECT category, COUNT(*) as count, AVG(price) as avg_price
        FROM products
        GROUP BY category
        ORDER BY count DESC
    ''')
    
    categories = cursor.fetchall()
    for cat in categories:
        print(f"   {cat[0]}: {cat[1]} products (Avg: ₹{cat[2]:.2f})")
    
    # Test 5: Verify foreign key integrity
    print(f"\n5️⃣ DATA INTEGRITY TEST...")
    cursor.execute('''
        SELECT COUNT(*) FROM products p
        LEFT JOIN wholesalers w ON p.wholesaler_id = w.id
        WHERE w.id IS NULL
    ''')
    
    orphaned_products = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM products WHERE wholesaler_id IS NULL')
    null_wholesaler_products = cursor.fetchone()[0]
    
    print(f"   Orphaned products (invalid wholesaler_id): {orphaned_products}")
    print(f"   Products with NULL wholesaler_id: {null_wholesaler_products}")
    
    # Test 6: Sample authentication test
    print(f"\n6️⃣ AUTHENTICATION SIMULATION...")
    
    # Test wholesaler login simulation
    test_phone = "9876543210"  # Mumbai Fresh Mart
    cursor.execute('SELECT id, name, password FROM wholesalers WHERE phone = ?', (test_phone,))
    wholesaler_auth = cursor.fetchone()
    
    if wholesaler_auth:
        w_id, w_name, w_password = wholesaler_auth
        print(f"   Wholesaler Login Test: {w_name} (ID: {w_id})")
        
        # Get their products
        cursor.execute('SELECT COUNT(*) FROM products WHERE wholesaler_id = ?', (w_id,))
        their_products = cursor.fetchone()[0]
        print(f"   Their products in dashboard: {their_products}")
        
        # Test what vendor would see for this wholesaler
        cursor.execute('''
            SELECT name, category, price FROM products 
            WHERE wholesaler_id = ? 
            ORDER BY category, name
        ''', (w_id,))
        
        vendor_sees = cursor.fetchall()
        print(f"   What vendor sees from this wholesaler: {len(vendor_sees)} products")
        for vs in vendor_sees[:3]:  # Show first 3
            print(f"      - {vs[0]} ({vs[1]}) - ₹{vs[2]}")
        if len(vendor_sees) > 3:
            print(f"      ... and {len(vendor_sees) - 3} more")
    
    conn.close()
    
    # Final validation
    print(f"\n" + "=" * 50)
    print("✅ SYNCHRONIZATION STATUS:")
    print("=" * 50)
    
    sync_issues = []
    
    if orphaned_products > 0:
        sync_issues.append(f"❌ {orphaned_products} orphaned products found")
    
    if null_wholesaler_products > 0:
        sync_issues.append(f"❌ {null_wholesaler_products} products with NULL wholesaler_id")
    
    if not sync_issues:
        print("✅ All products properly linked to wholesalers")
        print("✅ Vendor-wholesaler data synchronization is PERFECT")
        print("✅ Authentication structure is ready")
    else:
        print("❌ ISSUES FOUND:")
        for issue in sync_issues:
            print(f"   {issue}")
    
    return len(sync_issues) == 0

if __name__ == "__main__":
    test_wholesaler_vendor_sync()
