import sqlite3
import storage


def create_db():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpu INTEGER,
            memory_left REAL,
            used_ram REAL,
            virtual_memory INTEGER
        )
    ''')

    connection.commit()
    connection.close()


create_db()
storage.call_api()
