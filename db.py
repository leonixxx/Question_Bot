import aiosqlite
from aiogram import Bot, Dispatcher, F, types

dp = Dispatcher()
DB_NAME = "quiz_bot.db"


async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        # Создаем таблицу для состояния квиза
        await db.execute(
            """CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER)"""
        )

        # Создаем таблицу для результатов квиза
        await db.execute(
            """CREATE TABLE IF NOT EXISTS quiz_results (user_id INTEGER PRIMARY KEY, result INTEGER)"""
        )

        await db.commit()
