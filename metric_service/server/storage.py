import sqlite3
import requests


def call_api():
    response_API = requests.get('http://127.0.0.1:8000/show')
    data = response_API.json()

    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    for _ in range(10):
        for item in data["Data"]:
            cursor.execute('''
                INSERT INTO api_data (cpu, memory_left, used_ram,
                    virtual_memory)
                VALUES (?, ?, ?, ?)
        ''', (item.get("CPU"), item.get("Memory Left"), item.get("Used RAM"),
                item.get("Virtual Memory")))


connection.commit()
connection.close()
