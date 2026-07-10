"""
Generate beautiful gradient SVG product images locally for all products
that still have placeholder/beach images.
No external API needed - creates beautiful, unique images per category.
"""
import os
import re
import sqlite3

DATABASE_NAME = 'vendor_clubs.db'
IMAGES_FOLDER = os.path.join('my_app', 'static', 'uploads', 'products')
PLACEHOLDER_SIZE = 20928

# Emoji + gradient definitions per product keyword
PRODUCT_VISUALS = {
    # Vegetables
    'garlic': ('🧄', '#fef3c7', '#d97706'),
    'ginger': ('🫚', '#fef9c3', '#ca8a04'),
    'green chilli': ('🌶️', '#dcfce7', '#16a34a'),
    'coriander': ('🌿', '#d1fae5', '#059669'),
    'dhaniya': ('🌿', '#d1fae5', '#059669'),
    'mint': ('🍃', '#d1fae5', '#10b981'),
    'pudina': ('🍃', '#d1fae5', '#10b981'),
    'lemon': ('🍋', '#fef9c3', '#eab308'),
    'nimbu': ('🍋', '#fef9c3', '#eab308'),
    'lady finger': ('🟢', '#dcfce7', '#22c55e'),
    'bhindi': ('🟢', '#dcfce7', '#22c55e'),
    'brinjal': ('🍆', '#f3e8ff', '#9333ea'),
    'baingan': ('🍆', '#f3e8ff', '#9333ea'),
    'capsicum': ('🫑', '#dcfce7', '#16a34a'),
    'shimla mirch': ('🫑', '#dcfce7', '#16a34a'),
    'carrot': ('🥕', '#ffedd5', '#ea580c'),
    'gajar': ('🥕', '#ffedd5', '#ea580c'),
    'radish': ('🥬', '#f0fdf4', '#15803d'),
    'mooli': ('🥬', '#f0fdf4', '#15803d'),
    'spinach': ('🥬', '#d1fae5', '#059669'),
    'palak': ('🥬', '#d1fae5', '#059669'),
    'fenugreek': ('🌿', '#ecfccb', '#65a30d'),
    'methi': ('🌿', '#ecfccb', '#65a30d'),
    'beetroot': ('🟣', '#fce7f3', '#be185d'),
    'chukandar': ('🟣', '#fce7f3', '#be185d'),
    'sweet potato': ('🍠', '#ffedd5', '#c2410c'),
    'shakarkand': ('🍠', '#ffedd5', '#c2410c'),
    'pumpkin': ('🎃', '#ffedd5', '#ea580c'),
    'kaddu': ('🎃', '#ffedd5', '#ea580c'),
    'bottle gourd': ('🟢', '#d1fae5', '#059669'),
    'lauki': ('🟢', '#d1fae5', '#059669'),
    'bitter gourd': ('🟢', '#ecfccb', '#65a30d'),
    'karela': ('🟢', '#ecfccb', '#65a30d'),
    'ridge gourd': ('🟢', '#dcfce7', '#22c55e'),
    'turai': ('🟢', '#dcfce7', '#22c55e'),
    'green peas': ('🟢', '#d1fae5', '#059669'),
    'matar': ('🟢', '#d1fae5', '#059669'),
    'cucumber': ('🥒', '#d1fae5', '#059669'),
    'kheera': ('🥒', '#d1fae5', '#059669'),
    'spring onion': ('🧅', '#dcfce7', '#16a34a'),
    'mushroom': ('🍄', '#fef3c7', '#92400e'),
    'broccoli': ('🥦', '#d1fae5', '#059669'),
    'french beans': ('🫘', '#dcfce7', '#22c55e'),
    'zucchini': ('🥒', '#dcfce7', '#22c55e'),
    'colocasia': ('🟤', '#fef3c7', '#92400e'),
    'arbi': ('🟤', '#fef3c7', '#92400e'),
    'drumstick': ('🟢', '#dcfce7', '#16a34a'),
    'shevga': ('🟢', '#dcfce7', '#16a34a'),
    'pointed gourd': ('🟢', '#d1fae5', '#059669'),
    'parwal': ('🟢', '#d1fae5', '#059669'),
    'raw banana': ('🍌', '#fef9c3', '#ca8a04'),
    'kacha kela': ('🍌', '#fef9c3', '#ca8a04'),
    'potato': ('🥔', '#fef3c7', '#a16207'),
    'aloo': ('🥔', '#fef3c7', '#a16207'),
    'onion': ('🧅', '#fce7f3', '#be185d'),
    'pyaz': ('🧅', '#fce7f3', '#be185d'),
    'tomato': ('🍅', '#fee2e2', '#dc2626'),
    'tamatar': ('🍅', '#fee2e2', '#dc2626'),
    'cabbage': ('🥬', '#d1fae5', '#059669'),
    'cauliflower': ('🥦', '#f5f5f4', '#78716c'),
    'organic': ('🍅', '#fee2e2', '#dc2626'),

    # Dals & Pulses
    'toor dal': ('🫘', '#fef9c3', '#ca8a04'),
    'chana dal': ('🫘', '#fef3c7', '#d97706'),
    'moong dal': ('🫘', '#fef9c3', '#65a30d'),
    'urad dal': ('🫘', '#f5f5f4', '#44403c'),
    'masoor dal': ('🫘', '#fee2e2', '#dc2626'),
    'rajma': ('🫘', '#fecaca', '#b91c1c'),
    'kabuli': ('🫘', '#fef3c7', '#a16207'),
    'chickpea': ('🫘', '#fef3c7', '#a16207'),

    # Flours & Grains
    'poha': ('🍚', '#fef3c7', '#d97706'),
    'suji': ('🌾', '#fef9c3', '#ca8a04'),
    'semolina': ('🌾', '#fef9c3', '#ca8a04'),
    'besan': ('🌾', '#fef3c7', '#d97706'),
    'maida': ('🌾', '#f5f5f4', '#a8a29e'),
    'atta': ('🌾', '#fef3c7', '#a16207'),
    'rice flour': ('🌾', '#f5f5f4', '#a8a29e'),
    'corn flour': ('🌽', '#fef9c3', '#eab308'),
    'sabudana': ('⚪', '#f5f5f4', '#78716c'),

    # Dairy
    'milk': ('🥛', '#f0f9ff', '#0284c7'),
    'paneer': ('🧀', '#fefce8', '#ca8a04'),
    'curd': ('🥛', '#f0f9ff', '#0ea5e9'),
    'yogurt': ('🥛', '#f0f9ff', '#0ea5e9'),
    'butter': ('🧈', '#fef9c3', '#eab308'),
    'cheese': ('🧀', '#fef9c3', '#ca8a04'),
    'cream': ('🥛', '#fefce8', '#fbbf24'),
    'buttermilk': ('🥛', '#f0f9ff', '#38bdf8'),
    'ghee': ('🫕', '#fef3c7', '#d97706'),
    'mozzarella': ('🧀', '#fefce8', '#ca8a04'),
    'condensed': ('🥫', '#fef3c7', '#d97706'),

    # Bread & Bakery
    'bread': ('🍞', '#fef3c7', '#a16207'),
    'pav': ('🍞', '#fef3c7', '#92400e'),
    'burger bun': ('🍔', '#fef3c7', '#a16207'),
    'hot dog bun': ('🌭', '#fef3c7', '#a16207'),
    'naan': ('🫓', '#fef3c7', '#92400e'),
    'roti': ('🫓', '#fef3c7', '#92400e'),
    'paratha': ('🫓', '#fef3c7', '#a16207'),
    'pizza base': ('🍕', '#fee2e2', '#dc2626'),

    # Frozen & Ready
    'samosa': ('🥟', '#fef3c7', '#d97706'),
    'frozen paratha': ('🫓', '#dbeafe', '#2563eb'),
    'noodles': ('🍜', '#fef9c3', '#ca8a04'),
    'idli': ('⚪', '#f5f5f4', '#78716c'),
    'dosa': ('🫓', '#fef3c7', '#a16207'),
    'canned rajma': ('🥫', '#fee2e2', '#dc2626'),
    'canned chole': ('🥫', '#fef3c7', '#d97706'),
    'momos': ('🥟', '#f5f5f4', '#78716c'),
    'poha mix': ('🍚', '#fef3c7', '#d97706'),

    # Oils
    'sunflower oil': ('🌻', '#fef9c3', '#eab308'),
    'mustard oil': ('🫗', '#fef9c3', '#ca8a04'),
    'groundnut oil': ('🥜', '#fef3c7', '#a16207'),
    'olive oil': ('🫒', '#d1fae5', '#059669'),
    'coconut oil': ('🥥', '#f5f5f4', '#78716c'),

    # Sauces & Condiments
    'ketchup': ('🍅', '#fee2e2', '#dc2626'),
    'mayonnaise': ('🫙', '#fef9c3', '#eab308'),
    'soy sauce': ('🫗', '#44403c', '#78716c'),
    'vinegar': ('🫗', '#fef9c3', '#ca8a04'),

    # Snacks
    'chips': ('🍟', '#fef9c3', '#eab308'),
    'namkeen': ('🍘', '#fef3c7', '#d97706'),
    'biscuits': ('🍪', '#fef3c7', '#a16207'),
    'peanuts': ('🥜', '#fef3c7', '#92400e'),

    # Beverages
    'tea': ('🍵', '#d1fae5', '#059669'),
    'coffee': ('☕', '#fef3c7', '#78350f'),
    'soft drink': ('🥤', '#fee2e2', '#dc2626'),
    'mango juice': ('🥭', '#fef9c3', '#eab308'),
    'coconut water': ('🥥', '#d1fae5', '#059669'),

    # Spices
    'turmeric': ('🌾', '#fef9c3', '#eab308'),
    'haldi': ('🌾', '#fef9c3', '#eab308'),
    'red chilli': ('🌶️', '#fee2e2', '#dc2626'),
    'coriander powder': ('🌿', '#d1fae5', '#059669'),
    'cumin': ('🟤', '#fef3c7', '#92400e'),
    'jeera': ('🟤', '#fef3c7', '#92400e'),
    'garam masala': ('🫙', '#fef3c7', '#d97706'),
    'biryani masala': ('🍛', '#fef3c7', '#d97706'),
    'pav bhaji masala': ('🫙', '#fee2e2', '#dc2626'),
    'chaat masala': ('🫙', '#fef9c3', '#ca8a04'),
    'black pepper': ('⚫', '#f5f5f4', '#1c1917'),

    # Spreads & Jams
    'peanut butter': ('🥜', '#fef3c7', '#a16207'),
    'jam': ('🫙', '#fce7f3', '#be185d'),
    'honey': ('🍯', '#fef3c7', '#d97706'),
    'nutella': ('🍫', '#fef3c7', '#78350f'),
    'cheese spread': ('🧀', '#fef9c3', '#ca8a04'),
    'pickle': ('🫙', '#fef9c3', '#ca8a04'),

    # Rice & Grains
    'basmati': ('🍚', '#f5f5f4', '#78716c'),
    'sona masoori': ('🍚', '#f5f5f4', '#78716c'),
    'brown rice': ('🍚', '#fef3c7', '#92400e'),
    'wheat': ('🌾', '#fef3c7', '#a16207'),
    'jowar': ('🌾', '#fef3c7', '#92400e'),
    'sorghum': ('🌾', '#fef3c7', '#92400e'),
    'bajra': ('🌾', '#fef9c3', '#ca8a04'),
    'ragi': ('🌾', '#fef3c7', '#78350f'),
    'oats': ('🥣', '#fef3c7', '#a16207'),

    # Household
    'disposable plate': ('🍽️', '#f5f5f4', '#a8a29e'),
    'disposable cup': ('🥤', '#f5f5f4', '#a8a29e'),
    'aluminum foil': ('🫕', '#e2e8f0', '#64748b'),

    # Desserts
    'ice cream': ('🍨', '#fce7f3', '#ec4899'),
    'gulab jamun': ('🍩', '#fef3c7', '#92400e'),

    # Non-veg
    'chicken': ('🍗', '#ffedd5', '#ea580c'),
    'fish': ('🐟', '#dbeafe', '#2563eb'),
    'prawns': ('🦐', '#ffedd5', '#ea580c'),
    'shrimp': ('🦐', '#ffedd5', '#ea580c'),
    'mutton': ('🥩', '#fee2e2', '#dc2626'),
    'eggs': ('🥚', '#fef3c7', '#a16207'),
    'egg': ('🥚', '#fef3c7', '#a16207'),
}

def safe_name(name):
    s = re.sub(r'[^a-z0-9]', '_', name.lower()).strip('_')
    while '__' in s:
        s = s.replace('__', '_')
    return s

def get_visual(product_name):
    name_lower = product_name.lower()
    for key, value in PRODUCT_VISUALS.items():
        if key in name_lower:
            return value
    return ('📦', '#f1f5f9', '#64748b')  # Default fallback

def create_svg_image(emoji, bg_light, bg_dark, product_name, width=400, height=400):
    """Create a beautiful SVG product image with gradient background and emoji."""
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <radialGradient id="bg" cx="50%" cy="40%" r="65%">
      <stop offset="0%" style="stop-color:{bg_light};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{bg_dark};stop-opacity:0.15" />
    </radialGradient>
    <radialGradient id="glow" cx="50%" cy="45%" r="35%">
      <stop offset="0%" style="stop-color:white;stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:white;stop-opacity:0" />
    </radialGradient>
  </defs>
  <rect width="{width}" height="{height}" fill="url(#bg)" rx="16"/>
  <rect width="{width}" height="{height}" fill="url(#glow)" rx="16"/>
  <text x="50%" y="42%" dominant-baseline="central" text-anchor="middle" 
        font-size="120" filter="drop-shadow(0 4px 8px rgba(0,0,0,0.15))">{emoji}</text>
  <text x="50%" y="78%" dominant-baseline="central" text-anchor="middle" 
        font-family="system-ui, -apple-system, sans-serif" font-size="18" font-weight="600"
        fill="{bg_dark}" opacity="0.7">{product_name}</text>
</svg>'''
    return svg

def svg_to_png_via_html(svg_content, output_path):
    """Save SVG directly as .svg renamed to .jpg (browsers render SVG in img tags fine)."""
    # Actually, let's just save as SVG — but the DB expects .jpg paths.
    # We'll save as SVG and update the DB path to use .svg extension.
    # Actually, simplest: save as SVG and serve it. But image tags use .jpg.
    # Best: save the SVG content as an SVG file alongside the .jpg.
    # The cleanest: just overwrite the .jpg file with SVG content.
    # Browsers are smart enough to render SVG even with .jpg extension in <img> tags.
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)

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
        
        # Skip if already a real (non-placeholder, non-SVG) image
        if os.path.exists(local_path):
            size = os.path.getsize(local_path)
            if size != PLACEHOLDER_SIZE and size > 50000:
                # Likely a real photo (AI-generated PNG or downloaded)
                skipped += 1
                continue
        
        emoji, bg_light, bg_dark = get_visual(name)
        
        # Create display name (without parenthetical Hindi names)
        display_name = re.sub(r'\s*\(.*?\)', '', name).strip()
        if len(display_name) > 20:
            display_name = display_name[:18] + '…'
        
        svg = create_svg_image(emoji, bg_light, bg_dark, display_name)
        svg_to_png_via_html(svg, local_path)
        generated += 1
        print(f"[OK] {sn}.jpg - {name.encode('ascii', 'replace').decode()}")
    
    print(f"\nGenerated {generated} SVG product images, skipped {skipped} real photos.")

if __name__ == '__main__':
    generate_all()
