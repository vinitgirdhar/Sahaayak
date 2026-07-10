#!/usr/bin/env python3
"""
Test script to verify the updated vendor dashboard with categories
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from my_app import create_app
from my_app.db import init_db
import sqlite3

def test_categories_query():
    # Initialize the app and database
    app = create_app()
    init_db()
    
    # Test the categories query
    conn = sqlite3.connect('vendor_clubs.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Test the category query
    cursor.execute('''
        SELECT DISTINCT category FROM products WHERE category IS NOT NULL ORDER BY category
    ''')
    all_categories = [row['category'] for row in cursor.fetchall()]
    
    print(f"✅ Found {len(all_categories)} unique categories:")
    for category in all_categories:
        print(f"   - {category}")
    
    # Test the random products query
    cursor.execute('''
        SELECT 
            p.*, 
            w.name as wholesaler_name,
            w.trust_score,
            (p.price * 1.25) as original_price
        FROM products p
        JOIN wholesalers w ON p.wholesaler_id = w.id
        WHERE w.is_approved = 1 AND p.stock > 0
        ORDER BY RANDOM() LIMIT 8
    ''')
    budget_products = cursor.fetchall()
    
    print(f"✅ Found {len(budget_products)} random budget products")
    if budget_products:
        print(f"   Sample: {budget_products[0]['name']} - ₹{budget_products[0]['price']}")
    
    conn.close()
    return True

if __name__ == "__main__":
    test_categories_query()
