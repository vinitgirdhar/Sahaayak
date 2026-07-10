"""
Generate beautiful gradient PNG product images using Pillow.
Creates real image files (not SVG) that work with any content-type.
"""
import os
import re
import sqlite3
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

DATABASE_NAME = 'vendor_clubs.db'
IMAGES_FOLDER = os.path.join('my_app', 'static', 'uploads', 'products')
IMG_SIZE = 400

# Color palettes per product keyword: (bg_start_rgb, bg_end_rgb, accent_rgb)
PRODUCT_COLORS = {
    # Vegetables
    'garlic': ((254,243,199), (217,119,6), (146,64,14)),
    'ginger': ((254,249,195), (202,138,4), (133,77,14)),
    'green chilli': ((220,252,231), (22,163,106), (5,150,105)),
    'coriander': ((209,250,229), (5,150,105), (4,120,87)),
    'dhaniya': ((209,250,229), (5,150,105), (4,120,87)),
    'mint': ((209,250,229), (16,185,129), (5,150,105)),
    'pudina': ((209,250,229), (16,185,129), (5,150,105)),
    'lemon': ((254,249,195), (234,179,8), (161,98,7)),
    'nimbu': ((254,249,195), (234,179,8), (161,98,7)),
    'lady finger': ((220,252,231), (34,197,94), (22,163,74)),
    'bhindi': ((220,252,231), (34,197,94), (22,163,74)),
    'brinjal': ((243,232,255), (147,51,234), (107,33,168)),
    'baingan': ((243,232,255), (147,51,234), (107,33,168)),
    'capsicum': ((220,252,231), (22,163,74), (21,128,61)),
    'shimla mirch': ((220,252,231), (22,163,74), (21,128,61)),
    'carrot': ((255,237,213), (234,88,12), (194,65,12)),
    'gajar': ((255,237,213), (234,88,12), (194,65,12)),
    'radish': ((240,253,244), (21,128,61), (22,101,52)),
    'mooli': ((240,253,244), (21,128,61), (22,101,52)),
    'spinach': ((209,250,229), (5,150,105), (4,120,87)),
    'palak': ((209,250,229), (5,150,105), (4,120,87)),
    'fenugreek': ((236,252,203), (101,163,13), (77,124,15)),
    'methi': ((236,252,203), (101,163,13), (77,124,15)),
    'beetroot': ((252,231,243), (190,24,93), (157,23,77)),
    'chukandar': ((252,231,243), (190,24,93), (157,23,77)),
    'sweet potato': ((255,237,213), (194,65,12), (154,52,18)),
    'shakarkand': ((255,237,213), (194,65,12), (154,52,18)),
    'pumpkin': ((255,237,213), (234,88,12), (194,65,12)),
    'kaddu': ((255,237,213), (234,88,12), (194,65,12)),
    'bottle gourd': ((209,250,229), (5,150,105), (4,120,87)),
    'lauki': ((209,250,229), (5,150,105), (4,120,87)),
    'bitter gourd': ((236,252,203), (101,163,13), (77,124,15)),
    'karela': ((236,252,203), (101,163,13), (77,124,15)),
    'ridge gourd': ((220,252,231), (34,197,94), (22,163,74)),
    'turai': ((220,252,231), (34,197,94), (22,163,74)),
    'green peas': ((209,250,229), (5,150,105), (4,120,87)),
    'matar': ((209,250,229), (5,150,105), (4,120,87)),
    'cucumber': ((209,250,229), (5,150,105), (4,120,87)),
    'kheera': ((209,250,229), (5,150,105), (4,120,87)),
    'spring onion': ((220,252,231), (22,163,74), (21,128,61)),
    'mushroom': ((254,243,199), (146,64,14), (120,53,15)),
    'broccoli': ((209,250,229), (5,150,105), (4,120,87)),
    'french beans': ((220,252,231), (34,197,94), (22,163,74)),
    'zucchini': ((220,252,231), (34,197,94), (22,163,74)),
    'colocasia': ((254,243,199), (146,64,14), (120,53,15)),
    'arbi': ((254,243,199), (146,64,14), (120,53,15)),
    'drumstick': ((220,252,231), (22,163,74), (21,128,61)),
    'shevga': ((220,252,231), (22,163,74), (21,128,61)),
    'pointed gourd': ((209,250,229), (5,150,105), (4,120,87)),
    'parwal': ((209,250,229), (5,150,105), (4,120,87)),
    'raw banana': ((254,249,195), (202,138,4), (133,77,14)),
    'kacha kela': ((254,249,195), (202,138,4), (133,77,14)),
    'potato': ((254,243,199), (161,98,7), (133,77,14)),
    'aloo': ((254,243,199), (161,98,7), (133,77,14)),
    'onion': ((252,231,243), (190,24,93), (157,23,77)),
    'pyaz': ((252,231,243), (190,24,93), (157,23,77)),
    'tomato': ((254,226,226), (220,38,38), (185,28,28)),
    'tamatar': ((254,226,226), (220,38,38), (185,28,28)),
    'cabbage': ((209,250,229), (5,150,105), (4,120,87)),
    'cauliflower': ((245,245,244), (120,113,108), (87,83,78)),
    'organic': ((254,226,226), (220,38,38), (185,28,28)),
    # Dals & Pulses
    'toor dal': ((254,249,195), (202,138,4), (161,98,7)),
    'chana dal': ((254,243,199), (217,119,6), (180,83,9)),
    'moong dal': ((254,249,195), (101,163,13), (77,124,15)),
    'urad dal': ((245,245,244), (68,64,60), (41,37,36)),
    'masoor dal': ((254,226,226), (220,38,38), (185,28,28)),
    'rajma': ((254,202,202), (185,28,28), (153,27,27)),
    'kabuli': ((254,243,199), (161,98,7), (133,77,14)),
    'chickpea': ((254,243,199), (161,98,7), (133,77,14)),
    # Flours
    'poha': ((254,243,199), (217,119,6), (180,83,9)),
    'suji': ((254,249,195), (202,138,4), (161,98,7)),
    'semolina': ((254,249,195), (202,138,4), (161,98,7)),
    'besan': ((254,243,199), (217,119,6), (180,83,9)),
    'maida': ((245,245,244), (168,162,158), (120,113,108)),
    'atta': ((254,243,199), (161,98,7), (133,77,14)),
    'rice flour': ((245,245,244), (168,162,158), (120,113,108)),
    'corn flour': ((254,249,195), (234,179,8), (202,138,4)),
    'sabudana': ((245,245,244), (120,113,108), (87,83,78)),
    # Dairy
    'milk': ((240,249,255), (2,132,199), (3,105,161)),
    'paneer': ((254,252,232), (202,138,4), (161,98,7)),
    'curd': ((240,249,255), (14,165,233), (2,132,199)),
    'yogurt': ((240,249,255), (14,165,233), (2,132,199)),
    'butter': ((254,249,195), (234,179,8), (202,138,4)),
    'cheese': ((254,249,195), (202,138,4), (161,98,7)),
    'cream': ((254,252,232), (251,191,36), (217,119,6)),
    'buttermilk': ((240,249,255), (56,189,248), (14,165,233)),
    'ghee': ((254,243,199), (217,119,6), (180,83,9)),
    'mozzarella': ((254,252,232), (202,138,4), (161,98,7)),
    'condensed': ((254,243,199), (217,119,6), (180,83,9)),
    # Bread
    'bread': ((254,243,199), (161,98,7), (133,77,14)),
    'pav': ((254,243,199), (146,64,14), (120,53,15)),
    'burger bun': ((254,243,199), (161,98,7), (133,77,14)),
    'hot dog bun': ((254,243,199), (161,98,7), (133,77,14)),
    'naan': ((254,243,199), (146,64,14), (120,53,15)),
    'roti': ((254,243,199), (146,64,14), (120,53,15)),
    'paratha': ((254,243,199), (161,98,7), (133,77,14)),
    'pizza base': ((254,226,226), (220,38,38), (185,28,28)),
    # Frozen
    'samosa': ((254,243,199), (217,119,6), (180,83,9)),
    'frozen paratha': ((219,234,254), (37,99,235), (29,78,216)),
    'noodles': ((254,249,195), (202,138,4), (161,98,7)),
    'idli': ((245,245,244), (120,113,108), (87,83,78)),
    'dosa': ((254,243,199), (161,98,7), (133,77,14)),
    'canned rajma': ((254,226,226), (220,38,38), (185,28,28)),
    'canned chole': ((254,243,199), (217,119,6), (180,83,9)),
    'momos': ((245,245,244), (120,113,108), (87,83,78)),
    'poha mix': ((254,243,199), (217,119,6), (180,83,9)),
    # Oils
    'sunflower oil': ((254,249,195), (234,179,8), (202,138,4)),
    'mustard oil': ((254,249,195), (202,138,4), (161,98,7)),
    'groundnut oil': ((254,243,199), (161,98,7), (133,77,14)),
    'olive oil': ((209,250,229), (5,150,105), (4,120,87)),
    'coconut oil': ((245,245,244), (120,113,108), (87,83,78)),
    # Sauces
    'ketchup': ((254,226,226), (220,38,38), (185,28,28)),
    'mayonnaise': ((254,249,195), (234,179,8), (202,138,4)),
    'soy sauce': ((68,64,60), (120,113,108), (87,83,78)),
    'vinegar': ((254,249,195), (202,138,4), (161,98,7)),
    # Snacks
    'chips': ((254,249,195), (234,179,8), (202,138,4)),
    'namkeen': ((254,243,199), (217,119,6), (180,83,9)),
    'biscuits': ((254,243,199), (161,98,7), (133,77,14)),
    'peanuts': ((254,243,199), (146,64,14), (120,53,15)),
    # Beverages
    'tea': ((209,250,229), (5,150,105), (4,120,87)),
    'coffee': ((254,243,199), (120,53,15), (69,26,3)),
    'soft drink': ((254,226,226), (220,38,38), (185,28,28)),
    'mango juice': ((254,249,195), (234,179,8), (202,138,4)),
    'coconut water': ((209,250,229), (5,150,105), (4,120,87)),
    # Spices
    'turmeric': ((254,249,195), (234,179,8), (202,138,4)),
    'haldi': ((254,249,195), (234,179,8), (202,138,4)),
    'red chilli': ((254,226,226), (220,38,38), (185,28,28)),
    'coriander powder': ((209,250,229), (5,150,105), (4,120,87)),
    'cumin': ((254,243,199), (146,64,14), (120,53,15)),
    'jeera': ((254,243,199), (146,64,14), (120,53,15)),
    'garam masala': ((254,243,199), (217,119,6), (180,83,9)),
    'biryani masala': ((254,243,199), (217,119,6), (180,83,9)),
    'pav bhaji masala': ((254,226,226), (220,38,38), (185,28,28)),
    'chaat masala': ((254,249,195), (202,138,4), (161,98,7)),
    'black pepper': ((245,245,244), (28,25,23), (68,64,60)),
    # Spreads
    'peanut butter': ((254,243,199), (161,98,7), (133,77,14)),
    'jam': ((252,231,243), (190,24,93), (157,23,77)),
    'honey': ((254,243,199), (217,119,6), (180,83,9)),
    'nutella': ((254,243,199), (120,53,15), (69,26,3)),
    'cheese spread': ((254,249,195), (202,138,4), (161,98,7)),
    'pickle': ((254,249,195), (202,138,4), (161,98,7)),
    # Rice & Grains
    'basmati': ((245,245,244), (120,113,108), (87,83,78)),
    'sona masoori': ((245,245,244), (120,113,108), (87,83,78)),
    'brown rice': ((254,243,199), (146,64,14), (120,53,15)),
    'wheat': ((254,243,199), (161,98,7), (133,77,14)),
    'jowar': ((254,243,199), (146,64,14), (120,53,15)),
    'sorghum': ((254,243,199), (146,64,14), (120,53,15)),
    'bajra': ((254,249,195), (202,138,4), (161,98,7)),
    'ragi': ((254,243,199), (120,53,15), (69,26,3)),
    'oats': ((254,243,199), (161,98,7), (133,77,14)),
    # Household
    'disposable plate': ((245,245,244), (168,162,158), (120,113,108)),
    'disposable cup': ((245,245,244), (168,162,158), (120,113,108)),
    'aluminum foil': ((226,232,240), (100,116,139), (71,85,105)),
    # Desserts
    'ice cream': ((252,231,243), (236,72,153), (219,39,119)),
    'gulab jamun': ((254,243,199), (146,64,14), (120,53,15)),
    # Non-veg
    'chicken': ((255,237,213), (234,88,12), (194,65,12)),
    'fish': ((219,234,254), (37,99,235), (29,78,216)),
    'prawns': ((255,237,213), (234,88,12), (194,65,12)),
    'shrimp': ((255,237,213), (234,88,12), (194,65,12)),
    'mutton': ((254,226,226), (220,38,38), (185,28,28)),
    'eggs': ((254,243,199), (161,98,7), (133,77,14)),
    'egg': ((254,243,199), (161,98,7), (133,77,14)),
}

def safe_name(name):
    s = re.sub(r'[^a-z0-9]', '_', name.lower()).strip('_')
    while '__' in s:
        s = s.replace('__', '_')
    return s

def get_colors(product_name):
    name_lower = product_name.lower()
    for key, value in PRODUCT_COLORS.items():
        if key in name_lower:
            return value
    return ((241,245,249), (100,116,139), (71,85,105))

def create_radial_gradient(size, color_center, color_edge):
    """Create a radial gradient image."""
    img = Image.new('RGB', (size, size))
    cx, cy = size // 2, int(size * 0.4)
    max_dist = size * 0.7
    
    pixels = img.load()
    for y in range(size):
        for x in range(size):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            ratio = min(dist / max_dist, 1.0)
            r = int(color_center[0] * (1 - ratio) + color_edge[0] * ratio)
            g = int(color_center[1] * (1 - ratio) + color_edge[1] * ratio)
            b = int(color_center[2] * (1 - ratio) + color_edge[2] * ratio)
            pixels[x, y] = (r, g, b)
    return img

def create_product_image(product_name, bg_start, bg_end, accent, size=400):
    """Create a beautiful product placeholder image."""
    # Create gradient background
    img = create_radial_gradient(size, bg_start, bg_end)
    draw = ImageDraw.Draw(img)
    
    # Add subtle white glow overlay in center
    overlay = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    center = size // 2
    for r in range(120, 0, -1):
        alpha = int(40 * (1 - r / 120))
        overlay_draw.ellipse(
            [center - r, int(size * 0.35) - r, center + r, int(size * 0.35) + r],
            fill=(255, 255, 255, alpha)
        )
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    draw = ImageDraw.Draw(img)
    
    # Add decorative circle
    circle_color = (
        min(255, bg_end[0] + 30),
        min(255, bg_end[1] + 30),
        min(255, bg_end[2] + 30),
    )
    draw.ellipse([size//2-60, size//2-80, size//2+60, size//2+40], 
                 outline=circle_color, width=3)
    
    # Get display name
    display_name = re.sub(r'\s*\(.*?\)', '', product_name).strip()
    if len(display_name) > 22:
        display_name = display_name[:20] + '..'
    
    # Draw product name
    try:
        font = ImageFont.truetype("arial.ttf", 22)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
        font_small = font
    
    # Text background bar
    text_y = int(size * 0.78)
    draw.rectangle([0, text_y - 15, size, text_y + 25], fill=(255, 255, 255, 80))
    
    # Draw text centered
    bbox = draw.textbbox((0, 0), display_name, font=font)
    text_width = bbox[2] - bbox[0]
    draw.text(((size - text_width) // 2, text_y - 10), display_name, 
              fill=accent, font=font)
    
    # Add a small label at top
    label = "SAHAAYAK"
    bbox2 = draw.textbbox((0, 0), label, font=font_small)
    lw = bbox2[2] - bbox2[0]
    draw.text(((size - lw) // 2, 15), label, fill=(*accent, 120) if len(accent) == 3 else accent, font=font_small)
    
    return img

def generate_all():
    os.makedirs(IMAGES_FOLDER, exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('SELECT DISTINCT name FROM products')
    names = [r[0] for r in c.fetchall()]
    conn.close()
    
    generated = 0
    skipped = 0
    
    for name in names:
        sn = safe_name(name)
        local_path = os.path.join(IMAGES_FOLDER, sn + '.jpg')
        
        # Skip AI-generated real photos (large file, not SVG text)
        if os.path.exists(local_path):
            size = os.path.getsize(local_path)
            # AI-generated PNGs are > 100KB, our Pillow images will be ~20-40KB
            # SVG text files from previous run are < 5KB
            # Original placeholders are exactly 20928 bytes
            if size > 50000:
                # Check it's not SVG text
                with open(local_path, 'rb') as f:
                    header = f.read(10)
                if not header.startswith(b'<?xml') and not header.startswith(b'<svg'):
                    skipped += 1
                    continue
        
        bg_start, bg_end, accent = get_colors(name)
        img = create_product_image(name, bg_start, bg_end, accent, IMG_SIZE)
        img.save(local_path, 'JPEG', quality=90)
        generated += 1
        safe_print = name.encode('ascii', 'replace').decode()
        print(f"[OK] {sn}.jpg - {safe_print}")
    
    print(f"\nGenerated {generated} PNG product images, skipped {skipped} real photos.")

if __name__ == '__main__':
    generate_all()
