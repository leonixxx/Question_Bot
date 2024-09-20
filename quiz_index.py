import aiosqlite

from db import DB_NAME, dp


async def get_quiz_index(user_id):
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute(
            "SELECT question_index FROM quiz_state WHERE user_id = (?)", (user_id,)
        ) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0


async def update_quiz_index(user_id, index):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute(
            "INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)",
            (user_id, index),
        )
        # Сохраняем изменения
        await db.commit()
