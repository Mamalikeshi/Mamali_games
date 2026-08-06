import aiosqlite

DATABASE_NAME = "mamali.db"


async def init_database():
    async with aiosqlite.connect(DATABASE_NAME) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(

            telegram_id INTEGER PRIMARY KEY,

            first_name TEXT,

            username TEXT,

            referral_code TEXT,

            balance REAL DEFAULT 0,

            total_games INTEGER DEFAULT 0,

            total_wins INTEGER DEFAULT 0,

            total_losses INTEGER DEFAULT 0,

            win_rate REAL DEFAULT 0

        )
        """)

        await db.commit()
