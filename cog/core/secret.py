# Standard imports
import os

# Third-party imports
from dotenv import load_dotenv
import mysql.connector


load_dotenv(f"{os.getcwd()}/.env")
DB_USER = os.getenv("MYSQL_USER")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
DB_NAME = os.getenv("MYSQL_DATABASE")
DB_HOST = os.getenv("HOST")
DB_PORT = os.getenv("MYSQL_PORT")


def connect():
    return mysql.connector.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
        port=DB_PORT,
    )
