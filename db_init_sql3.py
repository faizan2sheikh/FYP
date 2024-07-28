import sqlite3

# Connect to SQLite database (will create a new database if it doesn't exist)
conn = sqlite3.connect('object_occurrences.db')
cursor = conn.cursor()

# cursor.execute('''
#     DROP TABLE object_occurrences

# ''')

# Create table to store object occurrences
cursor.execute('''
    CREATE TABLE IF NOT EXISTS object_occurrences (
        frame_id TEXT PRIMARY KEY,
        object_class TEXT,
        timestamp TEXT,
        type TEXT
    )
''')

# Commit changes and close connection
conn.commit()
conn.close()
