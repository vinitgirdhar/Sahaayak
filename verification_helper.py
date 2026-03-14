import os
import re
import shutil
import sqlite3
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from my_app import create_app
from my_app import db as app_db


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DATABASE_PATH = PROJECT_ROOT / 'vendor_clubs.db'
SOURCE_STATIC_DIR = PROJECT_ROOT / 'my_app' / 'static'

LIVE_GEMINI_ENV_VAR = 'VERIFY_LIVE_GEMINI'

VERIFICATION_VENDOR = {
    'name': 'Verification Vendor',
    'email': 'verification.vendor@example.com',
    'phone': '9000000001',
    'password': 'verifyvendor',
    'alternate_contact': '9000000009',
    'shop_name': 'Verification Cart',
    'goods_type': 'Snacks',
    'working_hours': '06:00-14:00',
    'street_area': 'Verification Market',
    'pincode': '400001',
    'city': 'Mumbai',
    'location': 'Ghatkopar',
    'is_approved': 1,
}

VERIFICATION_WHOLESALERS = [
    {
        'name': 'Verification Wholesale Alpha',
        'phone': '9000000101',
        'password': 'verifyalpha',
        'shop_name': 'Alpha Wholesale',
        'sourcing_info': 'Fixture inventory for verification flows.',
        'location': 'Ghatkopar',
        'is_approved': 1,
    },
    {
        'name': 'Verification Wholesale Beta',
        'phone': '9000000102',
        'password': 'verifybeta',
        'shop_name': 'Beta Wholesale',
        'sourcing_info': 'Second approved wholesaler for split checkout coverage.',
        'location': 'Andheri',
        'is_approved': 1,
    },
    {
        'name': 'Verification Wholesale Pending',
        'phone': '9000000103',
        'password': 'verifypending',
        'shop_name': 'Pending Wholesale',
        'sourcing_info': 'Pending wholesaler used to verify login rejection.',
        'location': 'Kurla',
        'is_approved': 0,
    },
]

VERIFICATION_PRODUCTS = [
    {
        'wholesaler_phone': '9000000101',
        'name': 'Verification Chickpeas',
        'category': 'Dry Ingredients',
        'price': 68.0,
        'stock': 120,
        'status': 'In Stock',
        'image_path': 'uploads/groceries.jpg',
    },
    {
        'wholesaler_phone': '9000000102',
        'name': 'Verification Cheese Cubes',
        'category': 'Dairy Products',
        'price': 145.0,
        'stock': 90,
        'status': 'In Stock',
        'image_path': 'uploads/groceries.jpg',
    },
    {
        'wholesaler_phone': '9000000102',
        'name': 'Verification Spice Box',
        'category': 'Spices & Condiments',
        'price': 90.0,
        'stock': 40,
        'status': 'Low Stock',
        'image_path': 'uploads/groceries.jpg',
    },
]

STATIC_REF_PATTERN = re.compile(r"""(?:src|href)=["'](/static/[^"']+)["']""", re.IGNORECASE)
CSS_STATIC_REF_PATTERN = re.compile(r"""url\((['"]?)(/static/[^)'"]+)\1\)""", re.IGNORECASE)


@dataclass
class VerificationEnvironment:
    temp_root: Path
    database_path: Path
    static_dir: Path
    upload_dir: Path
    app: object


def status_for_stock(stock):
    if stock > 50:
        return 'In Stock'
    if stock > 0:
        return 'Low Stock'
    return 'Out of Stock'


def live_gemini_enabled():
    return os.getenv(LIVE_GEMINI_ENV_VAR) == '1'


def ensure_fixture_image(static_dir):
    uploads_dir = Path(static_dir) / 'uploads'
    uploads_dir.mkdir(parents=True, exist_ok=True)
    fixture_image = uploads_dir / 'groceries.jpg'
    if not fixture_image.exists():
        fixture_image.write_bytes(b'fixture-image')
    return fixture_image


def _copy_database(source_path, destination_path):
    if Path(source_path).exists():
        shutil.copy2(source_path, destination_path)
    else:
        sqlite3.connect(destination_path).close()


def _copy_static_tree(destination_path):
    if SOURCE_STATIC_DIR.exists():
        shutil.copytree(SOURCE_STATIC_DIR, destination_path)
    else:
        Path(destination_path).mkdir(parents=True, exist_ok=True)


def _upsert_vendor(cursor, vendor):
    cursor.execute('SELECT id FROM vendors WHERE phone = ?', (vendor['phone'],))
    row = cursor.fetchone()
    values = (
        vendor['name'],
        vendor['email'],
        vendor['phone'],
        vendor['password'],
        vendor['alternate_contact'],
        vendor['shop_name'],
        vendor['goods_type'],
        vendor['working_hours'],
        vendor['street_area'],
        None,
        vendor['pincode'],
        vendor['city'],
        vendor['location'],
        vendor['is_approved'],
    )

    if row:
        cursor.execute(
            '''
            UPDATE vendors
            SET name = ?, email = ?, phone = ?, password = ?, alternate_contact = ?,
                shop_name = ?, goods_type = ?, working_hours = ?, street_area = ?,
                photo_path = ?, pincode = ?, city = ?, location = ?, is_approved = ?
            WHERE id = ?
            ''',
            values + (row[0],),
        )
        return row[0]

    cursor.execute(
        '''
        INSERT INTO vendors (
            name, email, phone, password, alternate_contact, shop_name, goods_type,
            working_hours, street_area, photo_path, pincode, city, location, is_approved
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        values,
    )
    return cursor.lastrowid


def _upsert_wholesaler(cursor, wholesaler):
    cursor.execute('SELECT id FROM wholesalers WHERE phone = ?', (wholesaler['phone'],))
    row = cursor.fetchone()
    values = (
        wholesaler['name'],
        wholesaler['phone'],
        wholesaler['password'],
        wholesaler['shop_name'],
        wholesaler['sourcing_info'],
        wholesaler['location'],
        wholesaler['is_approved'],
    )

    if row:
        cursor.execute(
            '''
            UPDATE wholesalers
            SET name = ?, phone = ?, password = ?, shop_name = ?, sourcing_info = ?,
                location = ?, is_approved = ?
            WHERE id = ?
            ''',
            values + (row[0],),
        )
        return row[0]

    cursor.execute(
        '''
        INSERT INTO wholesalers (
            name, phone, password, shop_name, sourcing_info, location, is_approved
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        values,
    )
    return cursor.lastrowid


def _upsert_product(cursor, wholesaler_id, product):
    cursor.execute(
        'SELECT id FROM products WHERE wholesaler_id = ? AND name = ?',
        (wholesaler_id, product['name']),
    )
    row = cursor.fetchone()
    values = (
        product['category'],
        product['price'],
        product['stock'],
        1,
        product['image_path'],
        0,
        0,
        product['status'],
    )

    if row:
        cursor.execute(
            '''
            UPDATE products
            SET category = ?, price = ?, stock = ?, group_buy_eligible = ?, image_path = ?,
                views = ?, likes = ?, status = ?
            WHERE id = ?
            ''',
            values + (row[0],),
        )
        return row[0]

    cursor.execute(
        '''
        INSERT INTO products (
            wholesaler_id, name, category, price, stock, group_buy_eligible,
            image_path, views, likes, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (wholesaler_id, product['name']) + values,
    )
    return cursor.lastrowid


def seed_verification_fixture(database_path, static_dir):
    ensure_fixture_image(static_dir)
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    _upsert_vendor(cursor, VERIFICATION_VENDOR)

    wholesaler_ids = {}
    for wholesaler in VERIFICATION_WHOLESALERS:
        wholesaler_ids[wholesaler['phone']] = _upsert_wholesaler(cursor, wholesaler)

    for product in VERIFICATION_PRODUCTS:
        wholesaler_id = wholesaler_ids[product['wholesaler_phone']]
        product = dict(product)
        product['status'] = status_for_stock(product['stock'])
        _upsert_product(cursor, wholesaler_id, product)

    conn.commit()
    conn.close()


@contextmanager
def verification_environment(seed_fixture=True):
    temp_root = Path(tempfile.mkdtemp(prefix='sahaayak_verify_'))
    database_path = temp_root / 'vendor_clubs.db'
    static_dir = temp_root / 'static'

    _copy_database(DEFAULT_DATABASE_PATH, database_path)
    _copy_static_tree(static_dir)

    upload_dir = static_dir / 'uploads'
    upload_dir.mkdir(parents=True, exist_ok=True)

    app = create_app(
        config_overrides={
            'TESTING': True,
            'DATABASE': str(database_path),
            'UPLOAD_FOLDER': str(upload_dir),
        },
        static_folder=str(static_dir),
    )

    with app.app_context():
        app_db.init_db()

    if seed_fixture:
        seed_verification_fixture(database_path, static_dir)

    try:
        yield VerificationEnvironment(
            temp_root=temp_root,
            database_path=database_path,
            static_dir=static_dir,
            upload_dir=upload_dir,
            app=app,
        )
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def fetch_fixture_snapshot(database_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute(
        '''
        SELECT name, phone, shop_name, is_approved
        FROM wholesalers
        WHERE phone IN (?, ?, ?)
        ORDER BY phone
        ''',
        tuple(item['phone'] for item in VERIFICATION_WHOLESALERS),
    )
    wholesalers = cursor.fetchall()

    cursor.execute(
        '''
        SELECT w.phone, p.name, p.category, p.price, p.stock
        FROM products p
        JOIN wholesalers w ON w.id = p.wholesaler_id
        WHERE w.phone IN (?, ?)
          AND p.name IN (?, ?, ?)
        ORDER BY w.phone, p.name
        ''',
        (
            VERIFICATION_WHOLESALERS[0]['phone'],
            VERIFICATION_WHOLESALERS[1]['phone'],
            VERIFICATION_PRODUCTS[0]['name'],
            VERIFICATION_PRODUCTS[1]['name'],
            VERIFICATION_PRODUCTS[2]['name'],
        ),
    )
    products = cursor.fetchall()

    cursor.execute(
        'SELECT name, phone, location, is_approved FROM vendors WHERE phone = ?',
        (VERIFICATION_VENDOR['phone'],),
    )
    vendor = cursor.fetchone()

    conn.close()
    return {
        'vendor': vendor,
        'wholesalers': wholesalers,
        'products': products,
    }


def extract_local_static_refs(html_text):
    refs = {match.group(1).split('?', 1)[0] for match in STATIC_REF_PATTERN.finditer(html_text)}
    refs.update(match.group(2).split('?', 1)[0] for match in CSS_STATIC_REF_PATTERN.finditer(html_text))
    return sorted(refs)


def resolve_local_reference(reference, static_dir):
    if not reference:
        return None

    value = str(reference).strip()
    if not value or value.startswith(('http://', 'https://', 'data:')):
        return None

    candidate = Path(value)
    if candidate.is_absolute():
        return candidate

    normalized = value.lstrip('/\\').replace('\\', '/')
    static_dir = Path(static_dir)
    candidates = []

    if normalized.startswith('static/'):
        candidates.append(static_dir / normalized.split('/', 1)[1])
    elif normalized.startswith('uploads/'):
        candidates.append(static_dir / normalized)
    else:
        candidates.append(PROJECT_ROOT / normalized)
        candidates.append(static_dir / normalized)

    return candidates[0]

