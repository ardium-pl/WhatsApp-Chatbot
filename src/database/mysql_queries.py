import aiomysql
from src.logger import mysql_logger
from .mysql_config import connection, cursor

# To be updated
def get_user_id(sender_phone_number):
    try:
        query = "SELECT id FROM users WHERE sender_phone_number = %s"
        data = (sender_phone_number,)

        cursor.execute(query, data)
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            raise RuntimeError("No matching ids found.")

    except Exception as e:
        mysql_logger.warning(f"❌ An error occurred during fetching a user id: {e}")
        raise RuntimeError("Cannot perform further queries without user_id")


async def insert_data_mysql(sender_phone_number, user_query, ai_answer):
    try:
        async with aiomysql.create_pool(host='your_host', port=3306,
                                        user='your_user', password='your_password',
                                        db='your_database') as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    # Get user id based on the user phone number
                    await cur.execute("SELECT id FROM users WHERE sender_phone_number = %s", (sender_phone_number,))
                    result = await cur.fetchone()

                    # Insert query-answer pair of the given user
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
