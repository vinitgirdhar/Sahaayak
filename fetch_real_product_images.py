"""
Real Product Image Fetcher for Sahaayak
========================================
Fetches real product images from Unsplash (free API).
Uses search queries based on product names to find relevant images.
"""

import sqlite3
import os
import requests
import time
from urllib.parse import quote

DATABASE_NAME = 'vendor_clubs.db'
IMAGES_FOLDER = 'my_app/static/uploads/products'

# Unsplash API - Free tier allows 50 requests/hour
# Using the demo/source API which doesn't require authentication
UNSPLASH_SOURCE_URL = "https://source.unsplash.com/400x400/?"

# Product search term mappings for better image results
PRODUCT_SEARCH_TERMS = {
    # Vegetables
    'organic tomatoes': 'fresh tomatoes',
    'fresh spinach': 'spinach leaves',
    'premium carrots': 'fresh carrots',
    'red onions': 'red onions',
    'green capsicum': 'green bell pepper',
    'fresh broccoli': 'broccoli',
    'cauliflower': 'cauliflower',
    'green beans': 'green beans',
    'cabbage': 'cabbage vegetable',
    'cucumber': 'fresh cucumber',
    'lady finger (okra)': 'okra vegetable',
    'bitter gourd': 'bitter gourd',
    'bottle gourd': 'bottle gourd',
    'pumpkin': 'pumpkin',
    'radish': 'radish vegetable',
    
    # Dairy
    'fresh milk (1l)': 'milk bottle',
    'paneer (200g)': 'paneer cheese',
    'curd/yogurt (400g)': 'yogurt bowl',
    'butter (100g)': 'butter block',
    'cheese slices (200g)': 'cheese slices',
    'cream (200ml)': 'cream dairy',
    'buttermilk (500ml)': 'buttermilk glass',
    'ghee (500g)': 'ghee jar',
    'mozzarella cheese': 'mozzarella cheese',
    'condensed milk': 'condensed milk',
    'skimmed milk (1l)': 'skim milk',
    'flavored yogurt': 'flavored yogurt',
    
    # Dry Ingredients
    'toor dal': 'toor dal lentils',
    'chana dal': 'chana dal',
    'moong dal': 'moong dal lentils',
    'urad dal': 'urad dal',
    'masoor dal': 'red lentils',
    'rajma (kidney beans)': 'kidney beans',
    'kabuli chana': 'chickpeas',
    'poha (flattened rice)': 'poha flakes',
    'suji (semolina)': 'semolina',
    'besan (gram flour)': 'gram flour',
    'maida (all purpose flour)': 'all purpose flour',
    'atta (whole wheat)': 'wheat flour',
    'rice flour': 'rice flour',
    'corn flour': 'corn flour',
    'sabudana': 'tapioca pearls',
    
    # Bread & Bakery
    'white bread': 'white bread loaf',
    'brown bread': 'brown bread',
    'pav (dinner rolls) 6pc': 'dinner rolls bread',
    'burger buns 4pc': 'burger buns',
    'hot dog buns 4pc': 'hot dog buns',
    'croissant 2pc': 'croissants',
    'rusk pack': 'rusk biscuits',
    'naan (5pc)': 'naan bread',
    'roti (10pc)': 'roti flatbread',
    'paratha (5pc)': 'paratha bread',
    'pizza base (2pc)': 'pizza base',
    'garlic bread': 'garlic bread',
    
    # Oils & Condiments
    'sunflower oil (1l)': 'sunflower oil bottle',
    'mustard oil (1l)': 'mustard oil',
    'groundnut oil (1l)': 'peanut oil',
    'olive oil (500ml)': 'olive oil bottle',
    'coconut oil (500ml)': 'coconut oil',
    'sesame oil (200ml)': 'sesame oil',
    'tomato ketchup (500g)': 'tomato ketchup bottle',
    'mayonnaise (250g)': 'mayonnaise jar',
    'soy sauce (200ml)': 'soy sauce bottle',
    'vinegar (500ml)': 'vinegar bottle',
    'green chutney': 'mint chutney',
    'tamarind paste': 'tamarind paste',
    
    # Snacks & Beverages
    'chips (large pack)': 'potato chips bag',
    'namkeen mix (500g)': 'indian snacks mix',
    'biscuits variety pack': 'biscuits cookies',
    'roasted peanuts (250g)': 'roasted peanuts',
    'makhana (fox nuts)': 'fox nuts makhana',
    'dry fruit mix (250g)': 'mixed dry fruits',
    'tea (250g)': 'tea leaves',
    'coffee (200g)': 'coffee beans',
    'green tea (25 bags)': 'green tea bags',
    'soft drink (2l)': 'soda bottle',
    'mango juice (1l)': 'mango juice',
    'coconut water (1l)': 'coconut water',
    'energy drink': 'energy drink can',
    'lassi (500ml)': 'lassi drink',
    
    # Spices
    'turmeric powder (100g)': 'turmeric powder',
    'red chilli powder (100g)': 'red chili powder',
    'coriander powder (100g)': 'coriander powder',
    'cumin seeds (100g)': 'cumin seeds',
    'garam masala (100g)': 'garam masala spices',
    'biryani masala (50g)': 'biryani spices',
    'pav bhaji masala (50g)': 'indian spices',
    'chaat masala (100g)': 'chaat masala',
    'black pepper (50g)': 'black pepper',
    'cinnamon sticks (50g)': 'cinnamon sticks',
    'cardamom (25g)': 'cardamom pods',
    'cloves (25g)': 'cloves spice',
    'bay leaves (20g)': 'bay leaves',
    'mustard seeds (100g)': 'mustard seeds',
    'fenugreek seeds (100g)': 'fenugreek seeds',
    
    # Spreads & Pantry
    'peanut butter (250g)': 'peanut butter jar',
    'jam mixed fruit (250g)': 'fruit jam jar',
    'honey (250g)': 'honey jar',
    'nutella (350g)': 'chocolate spread',
    'cheese spread (200g)': 'cheese spread',
    'pickle (mango) 500g': 'mango pickle',
    'pickle (mixed) 500g': 'indian pickle',
    'chyawanprash (500g)': 'chyawanprash',
    'maple syrup (250ml)': 'maple syrup',
    'tahini (200g)': 'tahini paste',
    
    # Grains & Cereals
    'basmati rice (1kg)': 'basmati rice',
    'sona masoori rice (1kg)': 'rice grains',
    'brown rice (1kg)': 'brown rice',
    'wheat (1kg)': 'wheat grains',
    'jowar (sorghum) 500g': 'sorghum grains',
    'bajra (pearl millet) 500g': 'pearl millet',
    'ragi (finger millet) 500g': 'finger millet',
    'oats (500g)': 'oats cereal',
    'muesli (400g)': 'muesli cereal',
    'corn flakes (500g)': 'corn flakes',
    'quinoa (250g)': 'quinoa grains',
    'barley (500g)': 'barley grains',
    
    # Ready-to-Eat
    'frozen samosa (10pc)': 'samosa',
    'frozen paratha (5pc)': 'frozen paratha',
    'instant noodles pack': 'instant noodles',
    'ready mix idli': 'idli',
    'ready mix dosa': 'dosa',
    'canned rajma masala': 'rajma curry',
    'canned chole': 'chole curry',
    'frozen veg momos (10pc)': 'momos dumplings',
    'instant poha mix': 'poha dish',
    'ready mix upma': 'upma',
    'frozen spring rolls (8pc)': 'spring rolls',
    'instant soup pack': 'soup bowl',
    
    # Other
    'disposable plates (50pc)': 'disposable plates',
    'disposable cups (50pc)': 'disposable cups',
    'aluminum foil roll': 'aluminum foil',
    'cling wrap': 'cling wrap',
    'paper napkins (100pc)': 'paper napkins',
    'ice cream (500ml)': 'ice cream',
    'gulab jamun mix': 'gulab jamun',
    'jalebi mix': 'jalebi sweet',
    'rasgulla (1kg tin)': 'rasgulla sweet',
    'chicken fresh (500g)': 'raw chicken',
    'fish fresh (500g)': 'fresh fish',
    'prawns (250g)': 'prawns shrimp',
    'eggs (12pc)': 'eggs carton',
    'mutton (500g)': 'raw mutton meat',
}

def get_search_term(product_name):
    """Get optimized search term for a product"""
    name_lower = product_name.lower()
    
    # Check direct mapping
    if name_lower in PRODUCT_SEARCH_TERMS:
        return PRODUCT_SEARCH_TERMS[name_lower]
    
    # Try partial matches
    for key, value in PRODUCT_SEARCH_TERMS.items():
        if key in name_lower or name_lower in key:
            return value
    
    # Default: use product name with 'food' suffix for better results
    return f"{product_name} food"

def download_unsplash_image(product_id, product_name, category):
    """Download a real product image from Unsplash"""
    try:
        os.makedirs(IMAGES_FOLDER, exist_ok=True)
        
        # Generate filename
        safe_name = "".join(c if c.isalnum() else "_" for c in product_name.lower())[:30]
        filename = f"product_{product_id}_{safe_name}.jpg"
        filepath = os.path.join(IMAGES_FOLDER, filename)
        
        # Get search term
        search_term = get_search_term(product_name)
        
        # Unsplash Source API - returns a random image matching the query
        url = f"{UNSPLASH_SOURCE_URL}{quote(search_term)}"
        
        # Download image with redirect following
        response = requests.get(url, timeout=15, allow_redirects=True)
        
        if response.status_code == 200 and len(response.content) > 1000:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"  ✓ Downloaded: {filename} (search: '{search_term}')")
            return f"uploads/products/{filename}"
        else:
            print(f"  ✗ Failed for {product_name} (status: {response.status_code})")
            return None
            
    except Exception as e:
        print(f"  ✗ Error for {product_name}: {e}")
        return None

def fetch_all_product_images():
    """Fetch real images for all products"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get all products
    cursor.execute('SELECT id, name, category, image_path FROM products ORDER BY category, name')
    products = cursor.fetchall()
    
    print(f"\n{'='*60}")
    print(f"REAL PRODUCT IMAGE FETCHER (Unsplash)")
    print(f"{'='*60}")
    print(f"Total products to process: {len(products)}")
    print(f"Note: Unsplash free tier allows 50 requests/hour")
    print(f"Adding 1 second delay between requests to be respectful\n")
    
    updated_count = 0
    failed_count = 0
    
    for i, (product_id, name, category, current_image) in enumerate(products):
        print(f"\n[{i+1}/{len(products)}] Processing: {name} ({category})")
        
        # Download new image
        image_path = download_unsplash_image(product_id, name, category)
        
        if image_path:
            # Update database
            cursor.execute('UPDATE products SET image_path = ? WHERE id = ?', (image_path, product_id))
            updated_count += 1
        else:
            failed_count += 1
        
        # Rate limiting - be respectful to free API
        time.sleep(1)
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"✓ Updated: {updated_count} products with real images")
    print(f"✗ Failed: {failed_count} products")
    print(f"Total processed: {len(products)} products")
    print(f"\nImages saved to: {IMAGES_FOLDER}/")

def fetch_single_category(category_name):
    """Fetch images for a single category only"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name, category FROM products WHERE category = ? ORDER BY name', (category_name,))
    products = cursor.fetchall()
    
    print(f"\nFetching images for category: {category_name}")
    print(f"Products to process: {len(products)}\n")
    
    for product_id, name, category in products:
        print(f"Processing: {name}")
        image_path = download_unsplash_image(product_id, name, category)
        
        if image_path:
            cursor.execute('UPDATE products SET image_path = ? WHERE id = ?', (image_path, product_id))
        
        time.sleep(1)
    
    conn.commit()
    conn.close()
    print("\nDone!")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # Fetch for specific category
        category = ' '.join(sys.argv[1:])
        fetch_single_category(category)
    else:
        # Fetch all
        fetch_all_product_images()
