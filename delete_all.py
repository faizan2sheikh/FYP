import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('object_occurrences.db')
cursor = conn.cursor()

def delete_all_objects():
    # Delete all rows from the object_occurrences table
    cursor.execute('DELETE FROM object_occurrences')

    # Commit the transaction
    conn.commit()

# Call the function to delete all objects
delete_all_objects()

# Close database connection
conn.close()