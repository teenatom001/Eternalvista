# from db import get_db_connection

# def create_category_table():
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS category (
#             categoryid INT AUTO_INCREMENT PRIMARY KEY,
#             category VARCHAR(255) NOT NULL,
#             image VARCHAR(255)
#         )
#     """)

#     conn.commit()
#     conn.close()
