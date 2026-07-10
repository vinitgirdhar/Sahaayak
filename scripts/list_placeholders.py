import os
import sqlite3
import re

DATABASE_NAME = 'vendor_clubs.db'
PLACEHOLDER_SIZE = 20928

def safe_name(name):
    s = re.sub(r'[^a-z0-9]', '_', name.lower()).strip('_')
    while '__' in s:
        s = s.replace('__', '_')
    return s

conn = sqlite3.connect(DATABASE_NAME)
c = conn.cursor()
c.execute('SELECT DISTINCT name FROM products')
names = [r[0] for r in c.fetchall()]
conn.close()

still_placeholder = []
for n in names:
    sn = safe_name(n)
    path = os.path.join('my_app', 'static', 'uploads', 'products', sn + '.jpg')
    if not os.path.exists(path):
        still_placeholder.append(n)
    elif os.path.getsize(path) == PLACEHOLDER_SIZE:
        still_placeholder.append(n)

print(f"Products still using placeholder ({len(still_placeholder)}):")
for p in still_placeholder:
    print(f"  - {p}")
