import sqlite3

conn = sqlite3.connect("appointments_db.db")
print("Database created!")
conn.close()