from logger import logger_mysql
from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()


def connect_to_mysql():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=os.environ.get('MYSQL_HOST'),
            user=os.environ.get('MYSQL_USER'),
            port=os.environ.get('MYSQL_PORT'),
            password=os.environ.get('MYSQL_PASSWORD'),
            database=os.environ.get('MYSQL_DATABASE'),
        )

        if connection.is_connected():
            logger_mysql.info("✅ Successfully connected to the database.")

            cursor = connection.cursor()
            return connection, cursor

        else:
            raise RuntimeError("Database connection established but is not active.")

    except Exception as e:
        logger_mysql.critical("❌ Failed to establish a database connection")
        logger_mysql.critical(f"Error message: {e}")
        if connection:
            connection.close()
        return None, None


connection, cursor = connect_to_mysql()
