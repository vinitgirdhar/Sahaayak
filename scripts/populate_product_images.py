import sqlite3
import os
import requests
import time
from urllib.parse import quote

DATABASE_NAME = 'vendor_clubs.db'
IMAGES_FOLDER = 'my_app/static/uploads/products'

def populate_images():
    # 1. Create directory if missing
    os.makedirs(IMAGES_FOLDER, exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # 2. Get unique product names
    cursor.execute('SELECT DISTINCT name, category FROM products')
    unique_products = cursor.fetchall()
    
    print(f"\n=============================================")
    # ASCII checkmark replaced to avoid encoding errors
    print(f"DEDUPLICATED PRODUCT IMAGE SEEDER")
    print(f"=============================================")
    print(f"Unique products to process: {len(unique_products)}\n")
    
    downloaded_count = 0
    
    for i, (name, category) in enumerate(unique_products):
        # Create a clean safe name for filename & picsum seed
        safe_name = "".join(c if c.isalnum() else "_" for c in name.lower()).strip('_')
        while "__" in safe_name:
            safe_name = safe_name.replace("__", "_")
            
        filename = f"{safe_name}.jpg"
        filepath = os.path.join(IMAGES_FOLDER, filename)
        db_path = f"uploads/products/{filename}"
        
        # Check if already exists
        if os.path.exists(filepath):
            print(f"[{i+1}/{len(unique_products)}] Image already exists for: {name}")
        else:
            print(f"[{i+1}/{len(unique_products)}] Downloading image for: {name}...")
            # Use Picsum with safe_name as string seed for high-quality consistent image
            url = f"https://picsum.photos/seed/{safe_name}/400/400"
            try:
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(resp.content)
                    downloaded_count += 1
                else:
                    print(f"  [ERROR] Failed to download from Picsum (status {resp.status_code})")
            except Exception as e:
                print(f"  [ERROR] Exception: {e}")
                
            # Respectful delay
            time.sleep(0.1)
            
        # 3. Update database: all products with this name get the exact same image path!
        cursor.execute('UPDATE products SET image_path = ? WHERE name = ?', (db_path, name))
        
    conn.commit()
    conn.close()
    print(f"\n[SUCCESS] Completed. Downloaded {downloaded_count} new images. Database updated.")

if __name__ == '__main__':
    populate_images()
