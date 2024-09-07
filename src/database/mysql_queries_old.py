import asyncmy
from src.logger import mysql_logger
from src.config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE


async def insert_data_mysql(sender_phone_number, user_query, ai_answer):
    try:
        async with asyncmy.create_pool(
                host=MYSQL_HOST,
                port=int(MYSQL_PORT),
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                db=MYSQL_DATABASE
        ) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    try:
                        whatsapp_number_id = int(sender_phone_number)
                    except ValueError:
                        mysql_logger.error(f"❌ Invalid phone number format: {sender_phone_number}")
                        return

                    await cur.execute("SELECT id FROM users WHERE whatsapp_number_id = %s", (whatsapp_number_id,))
                    result = await cur.fetchone()

                    if not result:
                        mysql_logger.info("🔧 Message was sent by the unknown user. Adding new user to the database...")
                        await cur.execute("INSERT INTO users (whatsapp_number_id) VALUES (%s)", (whatsapp_number_id,))
                        await conn.commit()
                        mysql_logger.info("✅ New user added!")

                        # Retrieve the ID of the inserted row
                        await cur.execute("SELECT id FROM users WHERE whatsapp_number_id = %s", (whatsapp_number_id,))
                        result = await cur.fetchone()

                    if result:
                        user_id = result[0]
                        await cur.execute("INSERT INTO queries (user_id, query, answer) VALUES (%s, %s, %s)",
                                          (user_id, user_query, ai_answer))
                        await conn.commit()
                        mysql_logger.info("✅ New record inserted successfully into MySQL.")
                    else:
                        mysql_logger.warning(f"❌ No matching user found for WhatsApp number ID: {whatsapp_number_id}")
    except Exception as e:
        mysql_logger.error(f"❌ An error occurred during MySQL operation: {e}")


async def get_recent_queries(sender_phone_number):
    try:
        async with asyncmy.create_pool(
                host=MYSQL_HOST,
                port=int(MYSQL_PORT),
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                db=MYSQL_DATABASE
        ) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    try:
                        whatsapp_number_id = int(sender_phone_number)
                    except ValueError:
                        mysql_logger.error(f"❌ Invalid phone number format: {sender_phone_number}")
                        return []

                    await cur.execute("""
                        SELECT q.query, q.answer
                        FROM queries q
                        JOIN users u ON q.user_id = u.id
                        WHERE u.whatsapp_number_id = %s
                        AND q.created_at >= NOW() - INTERVAL 2 HOUR
                        ORDER BY q.created_at DESC
                        LIMIT 5
                    """, (whatsapp_number_id,))
                    results = await cur.fetchall()
                    return [{"query": query, "answer": answer} for query, answer in results]
    except Exception as e:
        mysql_logger.error(f"❌ An error occurred while fetching recent queries: {e}")
        return []
