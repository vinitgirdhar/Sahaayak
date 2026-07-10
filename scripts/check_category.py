import sqlite3
import json

def check_category_products():
    # Connect to the database
    conn = sqlite3.connect('vendor_clubs.db')
    cursor = conn.cursor()
    
    # Check the 'Vegetables' category
    category_id = 'vegetables'
    wholesaler_category = 'Vegetables'
    
    # Execute the same query as in the app.py route
    cursor.execute('''
        SELECT p.*, w.name as wholesaler_name, w.location, w.trust_score 
        FROM products p 
        JOIN wholesalers w ON p.wholesaler_id = w.id 
        WHERE p.category = ? AND w.is_approved = 1 AND p.stock > 0
        ORDER BY w.trust_score DESC, p.views DESC
    ''', (wholesaler_category,))
    
    products = cursor.fetchall()
    print(f"Found {len(products)} products in {wholesaler_category} category")
    
    if products:
        # Print the column names
        cursor.execute("PRAGMA table_info(products)")
        product_columns = [row[1] for row in cursor.fetchall()]
        print("\nProduct columns:")
        for i, col in enumerate(product_columns):
            print(f"  {i}: {col}")
        
        # Print the first product's data structure
        print("\nFirst product data structure:")
        for i, value in enumerate(products[0]):
            print(f"  Index {i}: {value}")
        
        # Check if the expected indices for the template exist
        expected_indices = {
            'product_id': 0,
            'product_name': 2,
            'price': 4,
            'stock': 5,
            'image_path': 7,
            'status': 10,
            'wholesaler_name': 13,  # This might be different
            'location': 14,         # This might be different
            'trust_score': 16       # This might be different
        }
        
        print("\nChecking expected indices:")
        for name, idx in expected_indices.items():
            if idx < len(products[0]):
                print(f"  {name} (index {idx}): {products[0][idx]}")
            else:
                print(f"  {name} (index {idx}): OUT OF RANGE - max index is {len(products[0])-1}")
    
    conn.close()

if __name__ == "__main__":
    check_category_products()