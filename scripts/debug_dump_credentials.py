import sqlite3
from tabulate import tabulate

DB_PATH = 'vendor_clubs.db'

def fetch_all(query):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return rows

def main():
    vendors = fetch_all('SELECT id, name, phone, password, is_approved FROM vendors ORDER BY id')
    wholesalers = fetch_all('SELECT id, name, phone, password, is_approved FROM wholesalers ORDER BY id')

    if wholesalers:
        print('\nWholesalers:')
        print(tabulate(
            [(w[0], w[1], w[2], w[3], bool(w[4])) for w in wholesalers],
            headers=['id', 'name', 'phone', 'password', 'approved'],
            tablefmt='github'
        ))
    else:
        print('\nWholesalers: (none found)')

    if vendors:
        print('\nVendors:')
        print(tabulate(
            [(v[0], v[1], v[2], v[3], bool(v[4])) for v in vendors],
            headers=['id', 'name', 'phone', 'password', 'approved'],
            tablefmt='github'
        ))
    else:
        print('\nVendors: (none found)')

if __name__ == '__main__':
    main()
