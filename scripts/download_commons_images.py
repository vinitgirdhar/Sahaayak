import sqlite3
import os
import requests
import time
from urllib.parse import urlparse
from pathlib import Path

DATABASE_NAME = 'vendor_clubs.db'
IMAGES_FOLDER = 'my_app/static/uploads/products'
COMMONS_API_URL = 'https://commons.wikimedia.org/w/api.php'
REQUEST_HEADERS = {
    'User-Agent': 'SahaayakProductImageRefresh/1.0 (local development utility)'
}
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
PLACEHOLDER_SIZE = 20928
# Dictionary mapping product names to specific Wikimedia Commons search terms

PRODUCT_SEARCH_TERMS = {
    'potato (aloo)': 'potato bulb',
    'sweet potato (shakarkand)': 'sweet potato',
    'onion (pyaz)': 'red onion bulb',
    'tomato (tamatar)': 'tomato vegetable',
    'cabbage (patta gobi)': 'cabbage vegetable',
    'cauliflower (phool gobi)': 'cauliflower',
    'garlic (lahsun)': 'garlic bulb',
    'ginger (adrak)': 'ginger root',
    'green chillies (hari mirch)': 'green chili pepper',
    'coriander (dhaniya)': 'coriander leaves',
    'mint (pudina)': 'mint leaves',
    'lemon (nimbu)': 'lemon fruit',
    'lady finger (bhindi)': 'okra pod',
    'brinjal (baingan)': 'eggplant vegetable',
    'capsicum (shimla mirch)': 'bell pepper',
    'carrot (gajar)': 'carrot root',
    'radish (mooli)': 'radish root',
    'spinach (palak)': 'spinach leaves',
    'fenugreek (methi)': 'fenugreek leaves',
    'beetroot (chukandar)': 'beetroot',
    'pumpkin (kaddu)': 'pumpkin squash',
    'bottle gourd (lauki)': 'bottle gourd',
    'bitter gourd (karela)': 'bitter melon',
    'ridge gourd (turai)': 'ridge gourd',
    'green peas (matar)': 'green peas',
    'cucumber (kheera)': 'cucumber',
    'spring onion (pyaz patta)': 'scallion',
    'mushroom (button)': 'white button mushroom',
    'broccoli (premium)': 'broccoli head',
    'french beans': 'green beans',
    'zucchini (green)': 'zucchini',
    'colocasia root (arbi)': 'taro root',
    'drumstick (shevga)': 'drumstick tree pod',
    'pointed gourd (parwal)': 'pointed gourd',
    'raw banana (kacha kela)': 'green banana',
    # Dairy
    'fresh milk (1l)': 'milk bottle glass',
    'paneer (200g)': 'paneer cheese',
    'curd/yogurt (400g)': 'yogurt bowl',
    'butter (100g)': 'butter block',
    'cheese slices (200g)': 'cheese slices',
    'cream (200ml)': 'heavy cream bowl',
    'buttermilk (500ml)': 'buttermilk glass',
    'ghee (500g)': 'ghee jar',
    'mozzarella cheese (200g)': 'mozzarella',
    'condensed milk (400g)': 'condensed milk tin',
    # Bread
    'white bread (slab)': 'sliced white bread',
    'brown bread (slab)': 'whole wheat bread',
    'pav (dinner rolls) 6pc': 'dinner rolls',
    'burger buns 4pc': 'burger buns',
    'hot dog buns 4pc': 'hot dog buns',
    'naan (5pc pack)': 'naan bread',
    'roti (10pc pack)': 'roti flatbread',
    'paratha (5pc pack)': 'paratha flatbread',
    'pizza base (2pc pack)': 'pizza crust',
    # Ready-to-eat
    'frozen samosa (10pc)': 'samosa food',
    'frozen paratha (5pc)': 'paratha food',
    'instant noodles pack': 'ramen noodles pack',
    'ready mix idli (500g)': 'idli food',
    'ready mix dosa (500g)': 'dosa food',
    'canned rajma masala': 'kidney bean curry',
    'canned chole (chickpeas)': 'chickpea curry',
    'frozen veg momos (10pc)': 'dumplings',
    'instant poha mix (100g)': 'poha breakfast',
    # Packaging
    'disposable plates (50pc)': 'paper plates stack',
    'disposable cups (50pc)': 'paper cups stack',
    'aluminum foil roll': 'aluminum foil roll',
    # Desserts
    'ice cream (500ml)': 'vanilla ice cream scoop',
    'gulab jamun mix': 'gulab jamun bowl',
    # Seafood & Meat
    'chicken fresh (500g)': 'raw chicken breast',
    'fish fresh (500g)': 'raw fish fillet',
    'prawns (250g)': 'raw shrimp prawns',
    'mutton (500g)': 'raw mutton lamb meat',
    'eggs (12pc)': 'chicken eggs brown'
}

def get_search_term(product_name):
    name_lower = product_name.lower().strip()
    if name_lower in PRODUCT_SEARCH_TERMS:
        return PRODUCT_SEARCH_TERMS[name_lower]
    # Partial match
    for k, v in PRODUCT_SEARCH_TERMS.items():
        if k in name_lower or name_lower in k:
            return v
    return f"{product_name} food"

def search_commons_image(search_term):
    params = {
        'action': 'query',
        'generator': 'search',
        'gsrsearch': f'file: {search_term}',
        'gsrnamespace': '6',
        'prop': 'imageinfo',
        'iiprop': 'url',
        'iiurlwidth': 600,
        'format': 'json',
        'gsrlimit': 5,
    }
    try:
        resp = requests.get(COMMONS_API_URL, params=params, headers=REQUEST_HEADERS, timeout=15)
        if resp.status_code == 200:
            pages = resp.json().get('query', {}).get('pages', {})
            ranked = sorted(pages.values(), key=lambda p: p.get('index', 999))
            for page in ranked:
                info = (page.get('imageinfo') or [{}])[0]
                url = info.get('thumburl') or info.get('url')
                if url and Path(urlparse(url).path).suffix.lower() in SUPPORTED_EXTENSIONS:
                    return url, page.get('title')
    except Exception as e:
        print(f"    Search error: {e}")
    return None, None

def download_commons_images():
    os.makedirs(IMAGES_FOLDER, exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT name FROM products')
    unique_names = [r[0] for r in cursor.fetchall()]
    
    print(f"Total unique products: {len(unique_names)}")
    
    downloaded = 0
    skipped = 0
    for i, name in enumerate(unique_names):
        safe_name = "".join(c if c.isalnum() else "_" for c in name.lower()).strip('_')
        while "__" in safe_name:
            safe_name = safe_name.replace("__", "_")
            
        db_path = f"uploads/products/{safe_name}.jpg"
        local_path = os.path.join('my_app/static', db_path)
        
        # Check if the file is already a real downloaded image
        if os.path.exists(local_path) and os.path.getsize(local_path) != PLACEHOLDER_SIZE:
            skipped += 1
            continue
            
        search_term = get_search_term(name)
        print(f"[{i+1}/{len(unique_names)}] Downloading image for: {name}...")
        
        url, title = search_commons_image(search_term)
        if url:
            try:
                resp = requests.get(url, headers=REQUEST_HEADERS, timeout=15)
                if resp.status_code == 200:
                    with open(local_path, 'wb') as f:
                        f.write(resp.content)
                    downloaded += 1
                    safe_title = title.encode('ascii', 'ignore').decode('ascii')
                    print(f"  [SAVED] {db_path} from {safe_title}")
                else:
                    print(f"  [FAIL] Download status: {resp.status_code}")
            except Exception as e:
                print(f"  [ERROR] {e}")
        else:
            print("  [FAIL] No Commons image found")
            
        time.sleep(0.02)
        
    conn.close()
    print(f"\n[SUCCESS] Completed. Downloaded {downloaded} real product photos, skipped {skipped} already completed.")

if __name__ == '__main__':
    download_commons_images()
