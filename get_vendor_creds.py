import sqlite3

conn = sqlite3.connect('vendor_clubs.db')
cursor = conn.cursor()

cursor.execute('SELECT name, phone, password FROM vendors LIMIT 5')
vendors = cursor.fetchall()

print("VENDOR LOGIN CREDENTIALS:")
print("=" * 40)
for vendor in vendors:
    print(f"Name: {vendor[0]}")
    print(f"Phone: {vendor[1]}")
    print(f"Password: {vendor[2]}")
    print("-" * 25)

conn.close()
