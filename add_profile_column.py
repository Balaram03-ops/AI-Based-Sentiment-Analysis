import sqlite3


# =====================================================
# CONNECT TO DATABASE
# =====================================================

connection = sqlite3.connect("database.db")

cursor = connection.cursor()


# =====================================================
# CHECK EXISTING COLUMNS
# =====================================================

cursor.execute(
    "PRAGMA table_info(users)"
)

columns = cursor.fetchall()


column_names = [
    column[1]
    for column in columns
]


# =====================================================
# ADD PROFILE_PIC COLUMN
# =====================================================

if "profile_pic" not in column_names:

    cursor.execute(
        """
        ALTER TABLE users
        ADD COLUMN profile_pic VARCHAR(200)
        """
    )

    print(
        "profile_pic column added successfully!"
    )

else:

    print(
        "profile_pic column already exists!"
    )


# =====================================================
# SAVE CHANGES
# =====================================================

connection.commit()

connection.close()


print(
    "Database update completed."
)