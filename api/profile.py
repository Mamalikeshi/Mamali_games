import aiosqlite

from backend.config import DATABASE_NAME, DEFAULT_CURRENCY


async def register_or_get_user(
    telegram_id: int,
    first_name: str,
    username: str,
):
    async with aiosqlite.connect(DATABASE_NAME) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            "SELECT * FROM users WHERE telegram_id=?",
            (telegram_id,),
        )

        row = await cursor.fetchone()

        if row is None:
            await db.execute(
                """
                INSERT INTO users
                (telegram_id, first_name, username)
                VALUES (?, ?, ?)
                """,
                (
                    telegram_id,
                    first_name,
                    username,
                ),
            )

            await db.commit()

            cursor = await db.execute(
                "SELECT * FROM users WHERE telegram_id=?",
                (telegram_id,),
            )

            row = await cursor.fetchone()

        return dict(row)


async def get_profile(telegram_id: int):
    async with aiosqlite.connect(DATABASE_NAME) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            "SELECT * FROM users WHERE telegram_id=?",
            (telegram_id,),
        )

        row = await cursor.fetchone()

        if row is None:
            return None

        data = dict(row)
        data["currency"] = DEFAULT_CURRENCY

        return data
