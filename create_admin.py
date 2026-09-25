import mysql.connector
from werkzeug.security import generate_password_hash

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="gvgvjjb",
    database="sentiment_analysis"
)

cursor = conn.cursor()

name = "Admin"
email = "bffuujhv@gmail.com"
password = "xbhveb"

hashed_password = generate_password_hash(password)

sql = """
INSERT INTO admins (name, email, password)
VALUES (%s, %s, %s)
"""

values = (name, email, hashed_password)

try:
    cursor.execute(sql, values)
    conn.commit()

    print("====================================")
    print("ADMIN CREATED SUCCESSFULLY")
    print("====================================")
    print("Email    :", email)
    print("Password :", password)
    print("====================================")

except mysql.connector.Error as e:
    print("Error:", e)

finally:
    cursor.close()
    conn.close()
