from src.logger import mysql_logger as logger
from .mysql_config import connection, cursor


def get_user_id(whatsapp_number_id):
    try:
        query = "SELECT id FROM users WHERE whatsapp_number_id = %s"
        data = (whatsapp_number_id,)

        cursor.execute(query, data)
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            raise RuntimeError("No matching ids found.")

    except Exception as e:
        logger.warning(f"❌ An error occurred during fetching a user id: {e}")
        raise RuntimeError("Cannot perform further queries without user_id")


def insert_data_mysql(whatsapp_number_id, user_query, ai_answer):
    try:
        user_id = get_user_id(whatsapp_number_id)

        query = "INSERT INTO queries (user_id, query, answer) VALUES (%s, %s, %s)"
        data = (user_id, user_query, ai_answer)

        cursor.execute(query, data)
        connection.commit()

        if cursor.rowcount > 0:
            logger.info("✅ New record inserted successfully into MySQL.")
        else:
            logger.warning("❌ Failed to insert a new record into MySQL.")

    except Exception as e:
        logger.warning(f"❌ An error occurred during performing an insert query to MySQL: {e}")
