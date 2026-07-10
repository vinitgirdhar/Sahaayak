#!/usr/bin/env python3
"""
Check current database categories and products
"""

import sqlite3

def check_categories():
    conn = sqlite3.connect('vendor_clubs.db')
    cursor = conn.cursor()

    print('=== CURRENT CATEGORIES IN DATABASE ===')
    cursor.execute('SELECT DISTINCT category, COUNT(*) as count FROM products GROUP BY category ORDER BY category')
    categories = cursor.fetchall()
    for cat in categories:
        print(f'{cat[0]}: {cat[1]} products')

    print('\n=== PRODUCTS THAT MIGHT BE BREAD/BAKERY ===')
    cursor.execute('''
        SELECT p.name, p.category, w.name as wholesaler 
        FROM products p 
        JOIN wholesalers w ON p.wholesaler_id = w.id 
        WHERE p.name LIKE '%bread%' OR p.name LIKE '%bakery%' OR p.name LIKE '%pav%' 
           OR p.name LIKE '%chapati%' OR p.name LIKE '%paratha%' OR p.name LIKE '%dosa%'
           OR p.name LIKE '%pizza base%' OR p.name LIKE '%pizza dough%'
           OR p.name LIKE '%biscuit%' OR p.name LIKE '%cake%' OR p.name LIKE '%cookie%'
        ORDER BY p.name
    ''')
    bread_items = cursor.fetchall()
    for item in bread_items:
        print(f'  {item[0]} ({item[1]}) - {item[2]}')

    print('\n=== PRODUCTS THAT MIGHT BE DRY INGREDIENTS ===')
    cursor.execute('''
        SELECT p.name, p.category, w.name as wholesaler 
        FROM products p 
        JOIN wholesalers w ON p.wholesaler_id = w.id 
        WHERE p.name LIKE '%flour%' OR p.name LIKE '%sugar%' OR p.name LIKE '%salt%' 
           OR p.name LIKE '%rice%' OR p.name LIKE '%dal%' OR p.name LIKE '%lentil%'
           OR p.name LIKE '%wheat%' OR p.name LIKE '%oats%' OR p.name LIKE '%quinoa%'
           OR p.name LIKE '%brown sugar%' OR p.name LIKE '%rock salt%' OR p.name LIKE '%jaggery%'
           OR p.category LIKE '%cereal%' OR p.category LIKE '%grain%'
        ORDER BY p.name
    ''')
    dry_items = cursor.fetchall()
    for item in dry_items:
        print(f'  {item[0]} ({item[1]}) - {item[2]}')

    print('\n=== CURRENT SPICE PRODUCTS ===')
    cursor.execute('''
        SELECT p.name, p.category, w.name as wholesaler 
        FROM products p 
        JOIN wholesalers w ON p.wholesaler_id = w.id 
        WHERE p.category LIKE '%spice%' OR p.category LIKE '%condiment%'
        ORDER BY p.name
    ''')
    spice_items = cursor.fetchall()
    for item in spice_items:
        print(f'  {item[0]} ({item[1]}) - {item[2]}')

    print('\n=== ALL PACKAGED FOOD ITEMS ===')
    cursor.execute('''
        SELECT p.name, p.category, w.name as wholesaler 
        FROM products p 
        JOIN wholesalers w ON p.wholesaler_id = w.id 
        WHERE p.category = 'Packaged Foods'
        ORDER BY p.name
    ''')
    packaged_items = cursor.fetchall()
    for item in packaged_items:
        print(f'  {item[0]} ({item[1]}) - {item[2]}')

    conn.close()

if __name__ == "__main__":
    check_categories()
