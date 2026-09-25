import os
from urllib.parse import quote_plus


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)


# =========================================================
# FLASK CONFIGURATION
# =========================================================

class Config:

    # -----------------------------------------------------
    # SECRET KEY
    # -----------------------------------------------------

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-change-in-production"
    )


    # -----------------------------------------------------
    # MYSQL ENVIRONMENT VARIABLES
    # -----------------------------------------------------

    MYSQL_HOST = os.environ.get(
        "MYSQL_HOST",
        "localhost"
    )

    MYSQL_PORT = os.environ.get(
        "MYSQL_PORT",
        "3306"
    )

    MYSQL_DATABASE = os.environ.get(
        "MYSQL_DATABASE",
        "sentiment_analysis"
    )

    MYSQL_USER = os.environ.get(
        "MYSQL_USER",
        "root"
    )

    MYSQL_PASSWORD = os.environ.get(
        "MYSQL_PASSWORD",
        ""
    )


    # -----------------------------------------------------
    # ENCODE PASSWORD
    # -----------------------------------------------------

    encoded_password = quote_plus(MYSQL_PASSWORD)


    # -----------------------------------------------------
    # MYSQL DATABASE CONNECTION
    # -----------------------------------------------------

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+mysqlconnector://"
        f"{MYSQL_USER}:{encoded_password}@"
        f"{MYSQL_HOST}:{MYSQL_PORT}/"
        f"{MYSQL_DATABASE}"
    )


    # -----------------------------------------------------
    # SQLALCHEMY
    # -----------------------------------------------------

    SQLALCHEMY_TRACK_MODIFICATIONS = False