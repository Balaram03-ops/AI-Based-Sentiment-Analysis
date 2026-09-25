from werkzeug.security import generate_password_hash
import mysql.connector


# ==============================
# DATABASE CONNECTION
# ==============================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="AHrabss",
    database="sentiment_analysis"
)

cursor = db.cursor()


# ==============================
# ADMIN DETAILS
# ==============================

email = "gfshgdbb@ggbn"

new_password = "ngybjhg@vv"


# ==============================
# HASH PASSWORD
# ==============================

hashed_password = generate_password_hash(
    new_password
)


# ==============================
# UPDATE PASSWORD
# ==============================

sql = """
UPDATE admins
SET password = %s
WHERE email = %s
"""

cursor.execute(
    sql,
    (hashed_password, email)
)


# ==============================
# SAVE CHANGES
# ==============================

db.commit()


if cursor.rowcount > 0:

    print("======================================")
    print("ADMIN PASSWORD UPDATED SUCCESSFULLY")
    print("======================================")
    print("Email:", email)
    print("New Password:", new_password)

else:

    print("Admin account not found.")


cursor.close()
db.close()
