import os
import sqlite3


def execute_query(query, args=()):
    # db_path = os.path.join(os.getcwd(), 'chinook.db')
    with sqlite3.connect('chinook.db') as conn:
        cur = conn.cursor()
        cur.execute(query, args)
        conn.commit()
        records = cur.fetchall()
    return records
