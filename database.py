import mysql.connector
from config import db_config

def get_db_connection():
    """
    Establishes and returns a database connection.
    Prints an error and returns None if the connection fails.
    """
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Database Connection Error: {err}")
        return None
