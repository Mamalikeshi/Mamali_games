import aiosqlite

DATABASE_NAME = "mamali.db"


async def register_user(user):

    async with aiosqlite.connect(DATABASE_NAME) as db:

        cursor = await db.execute(
            "SELECT telegram_id FROM users WHERE telegram_id=?",
            (user.id,)
        )

        result = await cursor.fetchone()

        if result is None:

            await db.execute(
                """
                INSERT INTO users
                (telegram_id, first_name, username)
                VALUES (?, ?, ?)
                """,
                (
                    user.id,
                    user.first_name,
                    user.username
                )
            )

            await db.commit()
