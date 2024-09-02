import mysql.connector
import os
from dotenv import load_dotenv
from src.logger import mysql_logger as logger

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
            logger.info("✅ Successfully connected to the MySQL database.")
            cursor = connection.cursor()
            return connection, cursor
        else:
            raise RuntimeError("Database connection established but is not active.")

    except Exception as e:
        logger.critical(f"❌ Failed to establish a MySQL database connection: {e}")
        if connection:
            connection.close()
        return None, None


connection, cursor = connect_to_mysql()
