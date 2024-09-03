import aiomysql
from src.logger import mysql_logger
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
        mysql_logger.warning(f"❌ An error occurred during fetching a user id: {e}")
        raise RuntimeError("Cannot perform further queries without user_id")


async def insert_data_mysql(whatsapp_number_id, user_query, ai_answer):
    try:
        async with aiomysql.create_pool(host='your_host', port=3306,
                                        user='your_user', password='your_password',
                                        db='your_database') as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT id FROM users WHERE whatsapp_number_id = %s", (whatsapp_number_id,))
                    result = await cur.fetchone()
                    if result:
                        user_id = result[0]
                        await cur.execute("INSERT INTO queries (user_id, query, answer) VALUES (%s, %s, %s)",
                                          (user_id, user_query, ai_answer))
                        await conn.commit()
                        mysql_logger.info("✅ New record inserted successfully into MySQL.")
                    else:
                        mysql_logger.warning("❌ No matching user id found.")
    except Exception as e:
        mysql_logger.error(f"❌ An error occurred during MySQL operation: {e}")
