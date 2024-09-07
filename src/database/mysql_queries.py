import asyncmy
from src.logger import mysql_logger
from src.config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE


async def insert_data_mysql(sender_phone_number, user_query, ai_answer):
    try:
        # Używamy asyncmy.create_pool do utworzenia puli połączeń
        async with asyncmy.create_pool(
                host=MYSQL_HOST,
                port=int(MYSQL_PORT),
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                db=MYSQL_DATABASE
        ) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:

                    # Konwersja numeru telefonu do bigint
                    try:
                        whatsapp_number_id = int(sender_phone_number)
                    except ValueError:
                        mysql_logger.error(f"❌ Invalid phone number format: {sender_phone_number}")
                        return

                    # Pobieranie user_id na podstawie numeru telefonu
                    await cur.execute("SELECT id FROM users WHERE whatsapp_number_id = %s", (whatsapp_number_id,))
                    result = await cur.fetchone()

                    # Wprowadzenie numeru użytownika do tabeli users, jesli jeszcze go tam nie
                    if not result:
                        mysql_logger.info("🔧 Message was sent by the unknown user. Adding new user to the database...")
                        await cur.execute("INSERT INTO users (whatsapp_number_id) VALUES (%s)", (whatsapp_number_id,))
                        await conn.commit()
                        mysql_logger.info("✅ New user added!")

                        # Retrieve the ID of the inserted row - VERSION 1
                        new_user_id = await cur.lastrowid
                        mysql_logger.info(f"➡️ ID retrieved by the cur.lastrowid method: {new_user_id}.")

                        # Retrieve the ID of the inserted row - VERSION 2
                        await cur.execute("SELECT id FROM users WHERE whatsapp_number_id = %s", (whatsapp_number_id,))
                        result = await cur.fetchone()
                        mysql_logger.info(f"➡️ ID retrieved by the standard SELECT query: {result[0]}.")

                    # Wstawianie danych zapytania i odpowiedzi użytkownika
                    user_id = result[0]  # user_id jest intem
                    await cur.execute("INSERT INTO queries (user_id, query, answer) VALUES (%s, %s, %s)",
                                      (user_id, user_query, ai_answer))
                    await conn.commit()
                    mysql_logger.info("✅ New record inserted successfully into MySQL.")

    except Exception as e:
        mysql_logger.error(f"❌ An error occurred during MySQL operation: {e}")
