import mysql.connector
from mysql.connector import Error

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="eternalvista"
    )
    return connection


# ✅ TEST CONNECTION
if __name__ == "__main__":
    try:
        conn = get_db_connection()
        print("Database connected successfully!")
        conn.close()
    except Error as e:
        print("Connection failed:", e)
