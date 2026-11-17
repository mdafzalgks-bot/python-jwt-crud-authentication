import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


def get_connection():

    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=3306,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        connection_timeout=10
    )

    return conn
