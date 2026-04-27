import sqlite3

conn = sqlite3.connect('email_outreach.db')
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE emails ADD COLUMN scheduled_for DATETIME;")
    print("Column added successfully.")
except sqlite3.OperationalError as e:
    print("Error:", e)
conn.commit()
conn.close()
