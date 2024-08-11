# db_conn.py

import psycopg2
from psycopg2 import pool
import os

DATABASE_URL = os.getenv('DATABASE_URL')

# Create a connection pool
connection_pool = pool.SimpleConnectionPool(1, 20, DATABASE_URL)

def get_db_connection():
    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)
