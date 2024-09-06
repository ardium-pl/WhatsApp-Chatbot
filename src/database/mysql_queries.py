import aiomysql
from src.logger import mysql_logger
from src.config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE


# To be updated
# def get_user_id(sender_phone_number):


async def insert_data_mysql(sender_phone_number, user_query, ai_answer):
    try:
        async with aiomysql.create_pool(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                db=MYSQL_DATABASE
        ) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    # Get user id based on the user phone number
                    await cur.execute("SELECT id FROM users WHERE whatsapp_number_id = %s", (sender_phone_number,))
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
