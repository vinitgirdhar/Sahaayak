import sqlite3

# Connect to database
conn = sqlite3.connect('vendor_clubs.db')
cursor = conn.cursor()

# Update the vendor to be approved
cursor.execute('UPDATE vendors SET is_approved = 1 WHERE phone = ?', ('8378856546',))
print(f'Updated {cursor.rowcount} row(s)')

# Verify the change
cursor.execute('SELECT id, name, phone, is_approved FROM vendors WHERE phone = ?', ('8378856546',))
vendor = cursor.fetchone()
print(f'Vendor status: ID={vendor[0]}, Name={vendor[1]}, Phone={vendor[2]}, Approved={vendor[3]}')

conn.commit()
conn.close()
print('Database updated successfully!')
