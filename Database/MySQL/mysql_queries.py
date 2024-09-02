from logger import logger_mysql
from Database.MySQL.mysql_config import connection, cursor


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
        logger_mysql.warning("❌ An error occurred during fetching a user id.")
        logger_mysql.warning(f"Error message: {e}")
        raise RuntimeError("Cannot perform further queries without user_id")



def insert_data_mysql(whatsapp_number_id, user_query, ai_answer):
    try:
        user_id = get_user_id(whatsapp_number_id)

        query = "INSERT INTO queries (user_id, query, answer) VALUES (%s, %s, %s)"
        data = (user_id, user_query, ai_answer)

        cursor.execute(query, data)
        connection.commit()

        # Check if the insert was successful
        if cursor.rowcount > 0:
            logger_mysql.info("✅ New record inserted successfully.")
        else:
            logger_mysql.warning("❌ Failed to insert a new record.")

    except Exception as e:
        logger_mysql.warning("❌ An error occurred during performing an insert query.")
        logger_mysql.warning(f"Error message: {e}")
