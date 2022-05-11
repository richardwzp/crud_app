import datetime
import os
import sqlite3

from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        print(sqlite3.version)
    except Error as e:
        print(e)
        try:
            conn.close()
        except Error:
            pass
        raise e
    conn.execute("PRAGMA foreign_keys = 1")
    return conn


def create_database_instance():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "shopify.db")
    return create_connection(db_path)


if __name__ == '__main__':
    inst = create_connection("shopify.db")

