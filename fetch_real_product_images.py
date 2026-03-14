#!/usr/bin/env python3
"""
Refresh product images with relevant Wikimedia Commons photos.

This replaces the old random-image approach with Commons search so product cards
show the correct kind of item (tomatoes, onions, rice, tea, etc.).
"""

import argparse
import os
import sqlite3
import time
from pathlib import Path
from urllib.parse import urlparse

import requests


DATABASE_NAME = 'vendor_clubs.db'
STATIC_ROOT = Path('my_app/static')
IMAGES_FOLDER = STATIC_ROOT / 'uploads' / 'products'
COMMONS_API_URL = 'https://commons.wikimedia.org/w/api.php'
REQUEST_HEADERS = {
    'User-Agent': 'SahaayakProductImageRefresh/1.0 (local development utility)'
}
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

PRODUCT_SEARCH_TERMS = {
    'organic tomatoes': 'tomato vegetable',
    'fresh spinach': 'spinach leaves',
    'premium carrots': 'carrot vegetable',
    'red onions': 'red onion bulb',
    'green capsicum': 'green bell pepper',
    'fresh broccoli': 'broccoli vegetable',
    'cauliflower': 'cauliflower vegetable',
    'cucumber': 'cucumber vegetable',
    'basmati rice': 'basmati rice grains',
    'basmati rice (1kg)': 'basmati rice grains',
    'turmeric powder (100g)': 'turmeric powder spice',
    'cumin seeds (100g)': 'cumin seeds spice',
    'peanut butter (250g)': 'peanut butter jar',
    'tea (250g)': 'tea leaves',
    'sunflower oil (1l)': 'sunflower oil bottle',
    'mango juice (1l)': 'mango juice glass bottle',
}


def get_search_term(product_name):
    product_name_lower = product_name.lower()
    if product_name_lower in PRODUCT_SEARCH_TERMS:
        return PRODUCT_SEARCH_TERMS[product_name_lower]

    for key, value in PRODUCT_SEARCH_TERMS.items():
        if key in product_name_lower or product_name_lower in key:
            return value

    return f"{product_name} food product"


def is_supported_image_url(url):
    suffix = Path(urlparse(url).path).suffix.lower()
    return suffix in SUPPORTED_EXTENSIONS


def search_commons_image(search_term):
    params = {
        'action': 'query',
        'generator': 'search',
        'gsrsearch': f'file: {search_term}',
        'gsrnamespace': '6',
        'prop': 'imageinfo',
        'iiprop': 'url',
        'iiurlwidth': 960,
        'format': 'json',
        'gsrlimit': 8,
    }

    response = requests.get(
        COMMONS_API_URL,
        params=params,
        headers=REQUEST_HEADERS,
        timeout=20,
    )
    response.raise_for_status()

    pages = response.json().get('query', {}).get('pages', {})
    ranked_pages = sorted(pages.values(), key=lambda page: page.get('index', 9999))

    for page in ranked_pages:
        image_info = (page.get('imageinfo') or [{}])[0]
        preferred_url = image_info.get('thumburl') or image_info.get('url')
        if preferred_url and is_supported_image_url(preferred_url):
            return preferred_url, page.get('title')

    return None, None


def download_image(product_id, product_name, image_url):
    IMAGES_FOLDER.mkdir(parents=True, exist_ok=True)

    safe_name = ''.join(char if char.isalnum() else '_' for char in product_name.lower()).strip('_')
    extension = Path(urlparse(image_url).path).suffix.lower() or '.jpg'
    filename = f'product_{product_id}_{safe_name[:40]}{extension}'
    output_path = IMAGES_FOLDER / filename

    response = requests.get(image_url, headers=REQUEST_HEADERS, timeout=30)
    response.raise_for_status()
    output_path.write_bytes(response.content)

    return output_path, f"uploads/products/{filename}".replace('\\', '/')


def build_product_query(args):
    query = [
        'SELECT p.id, p.name, p.category',
        'FROM products p',
        'JOIN wholesalers w ON w.id = p.wholesaler_id',
    ]
    conditions = []
    params = []

    if args.wholesaler_phone:
        conditions.append('w.phone = ?')
        params.append(args.wholesaler_phone)

    if args.category:
        conditions.append('p.category = ?')
        params.append(args.category)

    if args.only_missing:
        conditions.append("(p.image_path IS NULL OR TRIM(p.image_path) = '' OR p.image_path = 'None')")

    if conditions:
        query.append('WHERE ' + ' AND '.join(conditions))

    query.append('ORDER BY p.category, p.name')
    return '\n'.join(query), params


def refresh_product_images(args):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    query, params = build_product_query(args)
    cursor.execute(query, params)
    products = cursor.fetchall()

    if not products:
        print('No matching products found.')
        conn.close()
        return 0

    print('SAHAAYAK PRODUCT IMAGE REFRESH')
    print('==============================')
    print(f'Products to process: {len(products)}')

    updated_count = 0
    failed_products = []

    for index, (product_id, product_name, category) in enumerate(products, start=1):
        search_term = get_search_term(product_name)
        print(f"[{index}/{len(products)}] {product_name} -> {search_term}")

        try:
            image_url, source_title = search_commons_image(search_term)
            if not image_url:
                failed_products.append((product_name, 'no usable Commons result'))
                print('  [FAIL] No matching Commons image found')
                continue

            _, db_path = download_image(product_id, product_name, image_url)
            cursor.execute('UPDATE products SET image_path = ? WHERE id = ?', (db_path, product_id))
            updated_count += 1
            print(f"  [PASS] Saved {db_path} from {source_title}")
        except Exception as exc:
            failed_products.append((product_name, str(exc)))
            print(f"  [FAIL] {exc}")

        time.sleep(args.delay)

    conn.commit()
    conn.close()

    print('')
    print('SUMMARY')
    print('-------')
    print(f'Updated: {updated_count}')
    print(f'Failed: {len(failed_products)}')
    for product_name, reason in failed_products[:10]:
        print(f'  - {product_name}: {reason}')

    return 1 if failed_products else 0


def parse_args():
    parser = argparse.ArgumentParser(description='Refresh product images with relevant Wikimedia Commons photos.')
    parser.add_argument('--wholesaler-phone', help='Only refresh products for this wholesaler phone number.')
    parser.add_argument('--category', help='Only refresh products in this category.')
    parser.add_argument('--only-missing', action='store_true', help='Only refresh products without an image_path.')
    parser.add_argument('--delay', type=float, default=0.4, help='Delay between requests in seconds.')
    return parser.parse_args()


if __name__ == '__main__':
    raise SystemExit(refresh_product_images(parse_args()))
