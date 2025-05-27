import sqlite3

conn = sqlite3.connect('faces.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS faces
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   encoding BLOB NOT NULL,
                   timestamp TEXT NOT NULL)''')
conn.commit()
conn.close()