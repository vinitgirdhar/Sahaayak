"""
Product Image Generator for Sahaayak
=====================================
Generates professional placeholder images for all products in the database.
Uses a combination of category-based colors and product-specific styling.
"""

import sqlite3
import os
import requests
from urllib.parse import quote

DATABASE_NAME = 'vendor_clubs.db'
IMAGES_FOLDER = 'my_app/static/uploads/products'

# Category color schemes (background color, text color)
CATEGORY_COLORS = {
    'vegetables': ('4CAF50', 'FFFFFF'),      # Green
    'Vegetables': ('4CAF50', 'FFFFFF'),
    'dry-ingredients': ('8D6E63', 'FFFFFF'), # Brown
    'Dry Ingredients': ('8D6E63', 'FFFFFF'),
    'dairy': ('2196F3', 'FFFFFF'),           # Blue
    'Dairy': ('2196F3', 'FFFFFF'),
    'breads': ('FF9800', 'FFFFFF'),          # Orange
    'Breads': ('FF9800', 'FFFFFF'),
    'Bakery': ('FF9800', 'FFFFFF'),
    'prepared': ('9C27B0', 'FFFFFF'),        # Purple
    'Prepared': ('9C27B0', 'FFFFFF'),
    'oils-sauces': ('F44336', 'FFFFFF'),     # Red
    'Oils & Sauces': ('F44336', 'FFFFFF'),
    'snacks': ('FFEB3B', '333333'),          # Yellow
    'Snacks': ('FFEB3B', '333333'),
    'spices': ('E91E63', 'FFFFFF'),          # Pink
    'Spices': ('E91E63', 'FFFFFF'),
    'spreads': ('795548', 'FFFFFF'),         # Dark Brown
    'Spreads': ('795548', 'FFFFFF'),
    'packaging': ('607D8B', 'FFFFFF'),       # Blue Grey
    'Packaging': ('607D8B', 'FFFFFF'),
    'grains': ('FFC107', '333333'),          # Amber
    'Grains': ('FFC107', '333333'),
    'beverage': ('00BCD4', 'FFFFFF'),        # Cyan
    'Beverages': ('00BCD4', 'FFFFFF'),
    'desserts': ('FF4081', 'FFFFFF'),        # Pink accent
    'Desserts': ('FF4081', 'FFFFFF'),
    'seafood-meat': ('D32F2F', 'FFFFFF'),    # Dark Red
    'Seafood & Meat': ('D32F2F', 'FFFFFF'),
}

# Default colors
DEFAULT_COLORS = ('6366F1', 'FFFFFF')  # Indigo

def get_image_prompt(product_name, category):
    """Generate AI image prompt for a product"""
    return f"Professional product photography of {product_name}, white background, studio lighting, realistic, high detail, no brand names, no text, no watermark"

def create_placeholder_image_url(product_name, category, size=400):
    """Create a placeholder image URL using placehold.co service"""
    bg_color, text_color = CATEGORY_COLORS.get(category, DEFAULT_COLORS)
    
    # Create a short display name (max 20 chars)
    display_name = product_name[:20] + '...' if len(product_name) > 20 else product_name
    display_name = quote(display_name)
    
    # Using placehold.co for placeholder images - explicitly request PNG format
    return f"https://placehold.co/{size}x{size}/{bg_color}/{text_color}.png?text={display_name}"

def download_placeholder_image(product_id, product_name, category):
    """Download and save a placeholder image for a product"""
    try:
        # Create images folder if it doesn't exist
        os.makedirs(IMAGES_FOLDER, exist_ok=True)
        
        # Generate image filename
        safe_name = "".join(c if c.isalnum() else "_" for c in product_name.lower())[:30]
        filename = f"product_{product_id}_{safe_name}.png"
        filepath = os.path.join(IMAGES_FOLDER, filename)
        
        # Check if image already exists
        if os.path.exists(filepath):
            print(f"  ✓ Image already exists: {filename}")
            return f"uploads/products/{filename}"
        
        # Download placeholder image
        url = create_placeholder_image_url(product_name, category)
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"  ✓ Downloaded: {filename}")
            return f"uploads/products/{filename}"
        else:
            print(f"  ✗ Failed to download image for {product_name}")
            return None
            
    except Exception as e:
        print(f"  ✗ Error downloading image for {product_name}: {e}")
        return None

def generate_all_product_images():
    """Generate placeholder images for all products in database"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Get all products
    cursor.execute('SELECT id, name, category, image_path FROM products ORDER BY category, name')
    products = cursor.fetchall()
    
    print(f"\n{'='*60}")
    print(f"PRODUCT IMAGE GENERATOR")
    print(f"{'='*60}")
    print(f"Total products to process: {len(products)}\n")
    
    updated_count = 0
    skipped_count = 0
    
    for product_id, name, category, current_image in products:
        print(f"\nProcessing: {name} ({category})")
        
        # Skip if already has a valid image
        if current_image and current_image != 'None' and os.path.exists(os.path.join('my_app/static', current_image)):
            print(f"  → Skipping (already has image)")
            skipped_count += 1
            continue
        
        # Download placeholder image
        image_path = download_placeholder_image(product_id, name, category)
        
        if image_path:
            # Update database with new image path
            cursor.execute('UPDATE products SET image_path = ? WHERE id = ?', (image_path, product_id))
            updated_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"✓ Updated: {updated_count} products")
    print(f"→ Skipped: {skipped_count} products (already had images)")
    print(f"Total processed: {len(products)} products")
    print(f"\nImages saved to: {IMAGES_FOLDER}/")

def store_image_prompts():
    """Store AI image generation prompts for all products (for future AI image generation)"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Check if image_prompt column exists, if not create it
    cursor.execute("PRAGMA table_info(products)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'image_prompt' not in columns:
        print("Adding image_prompt column to products table...")
        cursor.execute('ALTER TABLE products ADD COLUMN image_prompt TEXT')
    
    # Get all products
    cursor.execute('SELECT id, name, category FROM products')
    products = cursor.fetchall()
    
    print(f"\nStoring AI image prompts for {len(products)} products...")
    
    for product_id, name, category in products:
        prompt = get_image_prompt(name, category)
        cursor.execute('UPDATE products SET image_prompt = ? WHERE id = ?', (prompt, product_id))
    
    conn.commit()
    conn.close()
    
    print("✓ Image prompts stored successfully!")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--prompts-only':
        # Only store prompts without downloading images
        store_image_prompts()
    else:
        # Generate placeholder images
        generate_all_product_images()
        # Also store the AI prompts for future use
        store_image_prompts()
