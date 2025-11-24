
from db import get_db_connection

def create_category_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS category (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category_name VARCHAR(255) NOT NULL,
            image varchar
        )
    """)

    conn.commit()
    conn.close()
