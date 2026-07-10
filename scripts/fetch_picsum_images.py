"""
Real Product Image Fetcher for Sahaayak (Using Pixabay)
=======================================================
Fetches real product images from Pixabay (free API, no auth needed for small usage).
"""

import sqlite3
import os
import requests
import time
from urllib.parse import quote

DATABASE_NAME = 'vendor_clubs.db'
IMAGES_FOLDER = 'my_app/static/uploads/products'

# Product search term mappings for better image results
PRODUCT_SEARCH_TERMS = {
    # Vegetables
    'organic tomatoes': 'tomatoes fresh',
    'fresh spinach': 'spinach leaves green',
    'premium carrots': 'carrots fresh orange',
    'red onions': 'red onion',
    'green capsicum': 'green pepper vegetable',
    'fresh broccoli': 'broccoli green',
    'cauliflower': 'cauliflower white',
    'green beans': 'green beans vegetable',
    'cabbage': 'cabbage vegetable',
    'cucumber': 'cucumber green',
    'lady finger (okra)': 'okra vegetable',
    'bitter gourd': 'bitter melon',
    'bottle gourd': 'bottle gourd',
    'pumpkin': 'pumpkin orange',
    'radish': 'radish vegetable',
    
    # Dairy
    'fresh milk (1l)': 'milk glass',
    'paneer (200g)': 'cottage cheese',
    'curd/yogurt (400g)': 'yogurt bowl',
    'butter (100g)': 'butter',
    'cheese slices (200g)': 'cheese slices',
    'cream (200ml)': 'cream dairy',
    'buttermilk (500ml)': 'buttermilk',
    'ghee (500g)': 'ghee clarified butter',
    'mozzarella cheese': 'mozzarella',
    'condensed milk': 'condensed milk',
    'skimmed milk (1l)': 'milk',
    'flavored yogurt': 'yogurt fruit',
    
    # Dry Ingredients
    'toor dal': 'lentils yellow',
    'chana dal': 'chickpea split',
    'moong dal': 'mung beans',
    'urad dal': 'black gram',
    'masoor dal': 'red lentils',
    'rajma (kidney beans)': 'kidney beans',
    'kabuli chana': 'chickpeas',
    'poha (flattened rice)': 'rice flakes',
    'suji (semolina)': 'semolina',
    'besan (gram flour)': 'gram flour',
    'maida (all purpose flour)': 'flour white',
    'atta (whole wheat)': 'wheat flour',
    'rice flour': 'rice flour',
    'corn flour': 'cornstarch',
    'sabudana': 'tapioca pearls',
    
    # Bread & Bakery
    'white bread': 'bread loaf white',
    'brown bread': 'bread whole wheat',
    'pav (dinner rolls) 6pc': 'dinner rolls bread',
    'burger buns 4pc': 'burger buns',
    'hot dog buns 4pc': 'hot dog buns',
    'croissant 2pc': 'croissant',
    'rusk pack': 'rusk toast',
    'naan (5pc)': 'naan bread indian',
    'roti (10pc)': 'flatbread',
    'paratha (5pc)': 'paratha indian bread',
    'pizza base (2pc)': 'pizza dough',
    'garlic bread': 'garlic bread',    from my_app import create_app
    
    app = create_app()
    
    if __name__ == '__main__':
        app.run()
    
    # Oils & Condiments
    'sunflower oil (1l)': 'sunflower oil',
    'mustard oil (1l)': 'mustard oil',
    'groundnut oil (1l)': 'peanut oil',
    'olive oil (500ml)': 'olive oil bottle',
    'coconut oil (500ml)': 'coconut oil',
    'sesame oil (200ml)': 'sesame oil',
    'tomato ketchup (500g)': 'ketchup bottle',
    'mayonnaise (250g)': 'mayonnaise',
    'soy sauce (200ml)': 'soy sauce',
    'vinegar (500ml)': 'vinegar bottle',
    'green chutney': 'mint sauce',
    'tamarind paste': 'tamarind',
    
    # Snacks & Beverages
    'chips (large pack)': 'potato chips',
    'namkeen mix (500g)': 'indian snacks',
    'biscuits variety pack': 'cookies biscuits',
    'roasted peanuts (250g)': 'peanuts roasted',
    'makhana (fox nuts)': 'lotus seeds',
    'dry fruit mix (250g)': 'dried fruits mix',
    'tea (250g)': 'tea leaves',
    'coffee (200g)': 'coffee beans',
    'green tea (25 bags)': 'green tea',
    'soft drink (2l)': 'soda cola',
    'mango juice (1l)': 'mango juice',
    'coconut water (1l)': 'coconut water',
    'energy drink': 'energy drink',
    'lassi (500ml)': 'lassi yogurt drink',
    
    # Spices
    'turmeric powder (100g)': 'turmeric powder',
    'red chilli powder (100g)': 'chili powder red',
    'coriander powder (100g)': 'coriander powder',
    'cumin seeds (100g)': 'cumin seeds',
    'garam masala (100g)': 'indian spices',
    'biryani masala (50g)': 'spices mix',
    'pav bhaji masala (50g)': 'indian spices masala',
    'chaat masala (100g)': 'spice mix',
    'black pepper (50g)': 'black pepper',
    'cinnamon sticks (50g)': 'cinnamon sticks',
    'cardamom (25g)': 'cardamom',
    'cloves (25g)': 'cloves spice',
    'bay leaves (20g)': 'bay leaves',
    'mustard seeds (100g)': 'mustard seeds',
    'fenugreek seeds (100g)': 'fenugreek',
    
    # Spreads & Pantry
    'peanut butter (250g)': 'peanut butter',
    'jam mixed fruit (250g)': 'jam fruit',
    'honey (250g)': 'honey jar',
    'nutella (350g)': 'chocolate spread',
    'cheese spread (200g)': 'cream cheese spread',
    'pickle (mango) 500g': 'pickle indian',
    'pickle (mixed) 500g': 'pickled vegetables',
    'chyawanprash (500g)': 'ayurvedic jam',
    'maple syrup (250ml)': 'maple syrup',
    'tahini (200g)': 'tahini sesame',
    
    # Grains & Cereals
    'basmati rice (1kg)': 'basmati rice',
    'sona masoori rice (1kg)': 'rice grains',
    'brown rice (1kg)': 'brown rice',
    'wheat (1kg)': 'wheat grains',
    'jowar (sorghum) 500g': 'sorghum grains',
    'bajra (pearl millet) 500g': 'millet grains',
    'ragi (finger millet) 500g': 'millet finger',
    'oats (500g)': 'oats cereal',
    'muesli (400g)': 'muesli breakfast',
    'corn flakes (500g)': 'cornflakes cereal',
    'quinoa (250g)': 'quinoa',
    'barley (500g)': 'barley grains',
    
    # Ready-to-Eat
    'frozen samosa (10pc)': 'samosa indian',
    'frozen paratha (5pc)': 'paratha frozen',
    'instant noodles pack': 'instant noodles',
    'ready mix idli': 'idli south indian',
    'ready mix dosa': 'dosa crepe',
    'canned rajma masala': 'kidney bean curry',
    'canned chole': 'chickpea curry',
    'frozen veg momos (10pc)': 'dumplings',
    'instant poha mix': 'poha indian breakfast',
    'ready mix upma': 'upma south indian',
    'frozen spring rolls (8pc)': 'spring rolls',
    'instant soup pack': 'soup bowl',
    
    # Other
    'disposable plates (50pc)': 'disposable plates',
    'disposable cups (50pc)': 'paper cups',
    'aluminum foil roll': 'aluminum foil',
    'cling wrap': 'plastic wrap',
    'paper napkins (100pc)': 'napkins paper',
    'ice cream (500ml)': 'ice cream',
    'gulab jamun mix': 'gulab jamun indian sweet',
    'jalebi mix': 'jalebi indian sweet',
    'rasgulla (1kg tin)': 'rasgulla sweet',
    'chicken fresh (500g)': 'raw chicken',
    'fish fresh (500g)': 'fresh fish',
    'prawns (250g)': 'prawns shrimp',
    'eggs (12pc)': 'eggs',
    'mutton (500g)': 'lamb meat',
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
    
    # Default: use product name
    return product_name

def download_image_from_lorem_picsum(product_id, product_name, category):
    """Download a placeholder image with consistent seed"""
    try:
        os.makedirs(IMAGES_FOLDER, exist_ok=True)
        
        safe_name = "".join(c if c.isalnum() else "_" for c in product_name.lower())[:30]
        filename = f"product_{product_id}_{safe_name}.jpg"
        filepath = os.path.join(IMAGES_FOLDER, filename)
        
        # Use Lorem Picsum - free, no API key, reliable
        # Use product_id as seed for consistent images
        url = f"https://picsum.photos/seed/{product_id}/400/400"
        
        response = requests.get(url, timeout=15, allow_redirects=True)
        
        if response.status_code == 200 and len(response.content) > 1000:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"  ✓ Downloaded: {filename}")
            return f"uploads/products/{filename}"
        else:
            print(f"  ✗ Failed for {product_name} (status: {response.status_code})")
            return None
            
    except Exception as e:
        print(f"  ✗ Error for {product_name}: {e}")
        return None

def download_from_foodish(product_name, category):
    """Try to get food images from Foodish API (free, no auth)"""
    food_categories = {
        'Vegetables': 'https://foodish-api.com/api/images/rice',  # Closest available
        'Dairy Products': 'https://foodish-api.com/api/images/butter-chicken',
        'Bread & Bakery': 'https://foodish-api.com/api/images/burger',
        'Ready-to-Eat': 'https://foodish-api.com/api/images/biryani',
        'Snacks & Beverages': 'https://foodish-api.com/api/images/samosa',
        'Spices & Condiments': 'https://foodish-api.com/api/images/biryani',
    }
    
    url = food_categories.get(category, 'https://foodish-api.com/api/')
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('image')
    except:
        pass
    return None

def fetch_all_product_images():
    """Fetch images for all products using Lorem Picsum (reliable)"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name, category, image_path FROM products ORDER BY category, name')
    products = cursor.fetchall()
    
    print(f"\n{'='*60}")
    print(f"PRODUCT IMAGE FETCHER (Lorem Picsum)")
    print(f"{'='*60}")
    print(f"Total products to process: {len(products)}")
    print(f"Using Lorem Picsum for high-quality placeholder images\n")
    
    updated_count = 0
    failed_count = 0
    
    for i, (product_id, name, category, current_image) in enumerate(products):
        print(f"[{i+1}/{len(products)}] Processing: {name}")
        
        image_path = download_image_from_lorem_picsum(product_id, name, category)
        
        if image_path:
            cursor.execute('UPDATE products SET image_path = ? WHERE id = ?', (image_path, product_id))
            updated_count += 1
        else:
            failed_count += 1
        
        # Small delay to be respectful
        time.sleep(0.3)
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"✓ Updated: {updated_count} products")
    print(f"✗ Failed: {failed_count} products")
    print(f"Images saved to: {IMAGES_FOLDER}/")

if __name__ == '__main__':
    fetch_all_product_images()
