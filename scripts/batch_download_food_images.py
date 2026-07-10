"""
Download real food product images using Unsplash Source API (no API key needed).
Uses direct image URLs that return actual food photos.
"""
import os
import re
import sqlite3
import requests
import time

DATABASE_NAME = 'vendor_clubs.db'
IMAGES_FOLDER = os.path.join('my_app', 'static', 'uploads', 'products')
PLACEHOLDER_SIZE = 20928

# Direct Unsplash source queries for each product
SEARCH_QUERIES = {
    'garlic': 'garlic+cloves', 'ginger': 'ginger+root', 'green chillies': 'green+chili+pepper',
    'coriander': 'coriander+leaves+fresh', 'mint': 'mint+leaves+fresh', 'lemon': 'lemon+citrus',
    'lady finger': 'okra+vegetable', 'brinjal': 'eggplant+aubergine', 'capsicum': 'bell+pepper+colorful',
    'carrot': 'carrot+fresh', 'radish': 'radish+white', 'spinach': 'spinach+leaves',
    'fenugreek': 'fenugreek+leaves', 'beetroot': 'beetroot+red', 'sweet potato': 'sweet+potato',
    'pumpkin': 'pumpkin+squash', 'bottle gourd': 'bottle+gourd', 'bitter gourd': 'bitter+melon',
    'ridge gourd': 'ridge+gourd+vegetable', 'green peas': 'green+peas+fresh', 'cucumber': 'cucumber+fresh',
    'spring onion': 'spring+onion+scallion', 'mushroom': 'mushroom+white+button', 'broccoli': 'broccoli+fresh',
    'french beans': 'green+beans+fresh', 'zucchini': 'zucchini+courgette', 'colocasia': 'taro+root',
    'drumstick': 'drumstick+moringa', 'pointed gourd': 'pointed+gourd', 'raw banana': 'green+banana+plantain',
    'toor dal': 'toor+dal+lentils', 'chana dal': 'chana+dal+lentils', 'moong dal': 'moong+dal+yellow+lentils',
    'urad dal': 'urad+dal+black+lentils', 'masoor dal': 'red+lentils+masoor',
    'rajma': 'kidney+beans+red', 'kabuli chana': 'chickpeas+garbanzo', 'poha': 'flattened+rice+poha',
    'suji': 'semolina+rava', 'besan': 'gram+flour+besan', 'maida': 'flour+white+all+purpose',
    'atta': 'whole+wheat+flour', 'rice flour': 'rice+flour+white', 'corn flour': 'cornflour+yellow',
    'sabudana': 'tapioca+pearls+sago',
    'fresh milk': 'milk+bottle+glass', 'paneer': 'paneer+cheese+indian', 'curd': 'yogurt+curd+bowl',
    'butter': 'butter+block+yellow', 'cheese slices': 'cheese+slices', 'cream': 'cream+dairy+pouring',
    'buttermilk': 'buttermilk+glass', 'ghee': 'ghee+clarified+butter', 'mozzarella': 'mozzarella+cheese',
    'condensed milk': 'condensed+milk+tin',
    'white bread': 'white+bread+sliced', 'brown bread': 'whole+wheat+bread', 'pav': 'dinner+rolls+bread',
    'burger buns': 'burger+buns', 'hot dog buns': 'hot+dog+buns', 'naan': 'naan+bread+indian',
    'roti': 'roti+chapati+flatbread', 'paratha': 'paratha+indian+bread', 'pizza base': 'pizza+crust+base',
    'frozen samosa': 'samosa+indian+snack', 'frozen paratha': 'paratha+frozen', 'instant noodles': 'ramen+noodles+instant',
    'idli': 'idli+south+indian', 'dosa': 'dosa+south+indian', 'canned rajma': 'rajma+curry',
    'canned chole': 'chole+chickpea+curry', 'momos': 'momos+dumplings+steamed', 'poha mix': 'poha+breakfast',
    'sunflower oil': 'sunflower+oil+bottle', 'mustard oil': 'mustard+oil+bottle', 'groundnut oil': 'peanut+oil',
    'olive oil': 'olive+oil+bottle', 'coconut oil': 'coconut+oil+jar',
    'tomato ketchup': 'ketchup+tomato+sauce', 'mayonnaise': 'mayonnaise+jar', 'soy sauce': 'soy+sauce+bottle',
    'vinegar': 'vinegar+bottle',
    'chips': 'potato+chips+pack', 'namkeen': 'namkeen+indian+snacks', 'biscuits': 'biscuits+cookies+pack',
    'roasted peanuts': 'roasted+peanuts',
    'tea': 'tea+leaves+chai', 'coffee': 'coffee+beans+ground', 'soft drink': 'cola+soft+drink+bottle',
    'mango juice': 'mango+juice+glass', 'coconut water': 'coconut+water',
    'turmeric': 'turmeric+powder+haldi', 'red chilli powder': 'red+chili+powder', 'coriander powder': 'coriander+powder+spice',
    'cumin': 'cumin+seeds+jeera', 'garam masala': 'garam+masala+spice', 'biryani masala': 'biryani+spice+masala',
    'pav bhaji masala': 'pav+bhaji+masala', 'chaat masala': 'chaat+masala+spice', 'black pepper': 'black+pepper+peppercorn',
    'peanut butter': 'peanut+butter+jar', 'jam': 'fruit+jam+jar', 'honey': 'honey+jar+golden',
    'nutella': 'nutella+chocolate+spread', 'cheese spread': 'cheese+spread+jar', 'pickle': 'mango+pickle+indian',
    'basmati rice': 'basmati+rice+grain', 'sona masoori': 'rice+grain+white', 'brown rice': 'brown+rice+grain',
    'wheat': 'wheat+grain+whole', 'jowar': 'sorghum+grain', 'bajra': 'pearl+millet+grain',
    'ragi': 'finger+millet+grain', 'oats': 'oats+bowl+rolled',
    'disposable plates': 'paper+plates+disposable', 'disposable cups': 'paper+cups+disposable',
    'aluminum foil': 'aluminum+foil+roll',
    'ice cream': 'ice+cream+scoop+vanilla', 'gulab jamun': 'gulab+jamun+indian+dessert',
    'chicken': 'raw+chicken+breast+meat', 'fish': 'raw+fish+fillet+fresh', 'prawns': 'raw+shrimp+prawns',
    'mutton': 'raw+lamb+meat+mutton', 'eggs': 'eggs+brown+dozen',
    'organic tomatoes': 'tomato+organic+red', 'fresh spinach': 'spinach+fresh+green',
    'premium carrots': 'carrots+fresh+orange', 'red onions': 'red+onion+fresh',
    'green capsicum': 'green+bell+pepper', 'fresh broccoli': 'broccoli+head+green',
    'cauliflower': 'cauliflower+white+head',
}

def safe_name(name):
    s = re.sub(r'[^a-z0-9]', '_', name.lower()).strip('_')
    while '__' in s:
        s = s.replace('__', '_')
    return s

def find_query(product_name):
    name_lower = product_name.lower()
    for key, query in SEARCH_QUERIES.items():
        if key in name_lower:
            return query
    # Fallback: use the product name itself
    return '+'.join(product_name.lower().split()[:3]) + '+food'

def download_all():
    os.makedirs(IMAGES_FOLDER, exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('SELECT DISTINCT name FROM products')
    names = [r[0] for r in c.fetchall()]
    conn.close()
    
    downloaded = 0
    skipped = 0
    failed = 0
    
    for i, name in enumerate(names):
        sn = safe_name(name)
        local_path = os.path.join(IMAGES_FOLDER, sn + '.jpg')
        
        # Skip if already a real image (not placeholder)
        if os.path.exists(local_path) and os.path.getsize(local_path) != PLACEHOLDER_SIZE:
            skipped += 1
            continue
        
        query = find_query(name)
        url = f"https://source.unsplash.com/400x400/?{query}"
        
        print(f"[{i+1}/{len(names)}] {name} -> {query}...")
        
        try:
            resp = requests.get(url, timeout=15, allow_redirects=True)
            if resp.status_code == 200 and len(resp.content) > 5000:
                with open(local_path, 'wb') as f:
                    f.write(resp.content)
                downloaded += 1
                print(f"  [OK] Saved {sn}.jpg ({len(resp.content)} bytes)")
            else:
                failed += 1
                print(f"  [FAIL] status={resp.status_code} size={len(resp.content)}")
        except Exception as e:
            failed += 1
            print(f"  [ERROR] {e}")
        
        time.sleep(0.3)  # Be polite to Unsplash
    
    print(f"\nDone! Downloaded: {downloaded}, Skipped: {skipped}, Failed: {failed}")

if __name__ == '__main__':
    download_all()
