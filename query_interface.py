import sqlite3

def query_object_occurrences(object_class=None, start_time=None, end_time=None, input_type='live'):
    conn = sqlite3.connect('object_occurrences.db')
    cursor = conn.cursor()

    conditions = []
    query_params = []

    if object_class:
        conditions.append('object_class = ?')
        query_params.append(object_class)
    if start_time:
        conditions.append('timestamp >= ?')
        query_params.append(start_time)
    if end_time:
        conditions.append('timestamp <= ?')
        query_params.append(end_time)
    conditions.append('type = ?')
    query_params.append(input_type)

    query = 'SELECT frame_id FROM object_occurrences'
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    cursor.execute(query, query_params)
    results = cursor.fetchall()

    conn.close()
    return [result[0] for result in results] if results else []

# results = query_object_occurrences(object_class='bottle')
# print("Matching frame_ids:", results[-1])