"""Copy all AI-generated product images to the products folder."""
import shutil
import glob
import os

ARTIFACTS_DIR = r'C:\Users\vidhy\.gemini\antigravity-ide\brain\0edd81b5-02d9-4207-9d4b-89176a87bd91'
PRODUCTS_DIR = r'D:\Cooking stuff\Sahaayak\my_app\static\uploads\products'

# Map generated image prefix -> target filename in products folder
IMAGE_MAP = {
    'corn_flour_': 'corn_flour.jpg',
    'rice_flour_': 'rice_flour.jpg',
    'kabuli_chana_': 'kabuli_chana_chickpeas.jpg',
    'rajma_kidney_beans_': 'rajma_kidney_beans.jpg',
    'garlic_': 'garlic_lahsun.jpg',
    'ginger_': 'ginger_adrak.jpg',
    'green_chillies_': 'green_chillies_hari_mirch.jpg',
    'coriander_leaves_': 'coriander_dhaniya.jpg',
    'mint_leaves_': 'mint_pudina.jpg',
    'lemon_': 'lemon_nimbu.jpg',
    'okra_bhindi_': 'lady_finger_bhindi.jpg',
    'eggplant_baingan_': 'brinjal_baingan.jpg',
    'bell_pepper_': 'capsicum_shimla_mirch.jpg',
    'carrot_': 'carrot_gajar.jpg',
    'spinach_palak_': 'spinach_palak.jpg',
    'sweet_potato_': 'sweet_potato_shakarkand.jpg',
    'paneer_': 'paneer_200g.jpg',
}

# Also map to related product filenames that should share the same image
SHARED_IMAGES = {
    'carrot_': ['premium_carrots.jpg'],
    'spinach_palak_': ['fresh_spinach.jpg'],
    'bell_pepper_': ['green_capsicum.jpg'],
    'eggplant_baingan_': [],
    'coriander_leaves_': [],
    'lemon_': [],
    'sweet_potato_': [],
}

copied = 0
for prefix, target_name in IMAGE_MAP.items():
    matches = glob.glob(os.path.join(ARTIFACTS_DIR, f'{prefix}*.png'))
    if not matches:
        print(f"[SKIP] No generated image found for prefix: {prefix}")
        continue
    
    src = matches[0]
    dst = os.path.join(PRODUCTS_DIR, target_name)
    shutil.copy2(src, dst)
    copied += 1
    print(f"[OK] {target_name} <- {os.path.basename(src)}")
    
    # Copy to shared product filenames too
    for shared in SHARED_IMAGES.get(prefix, []):
        shared_dst = os.path.join(PRODUCTS_DIR, shared)
        shutil.copy2(src, shared_dst)
        copied += 1
        print(f"  [SHARED] {shared}")

print(f"\nCopied {copied} images total.")
