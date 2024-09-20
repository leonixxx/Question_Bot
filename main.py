import asyncio
import logging

import aiosqlite
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from db import DB_NAME, create_table, dp
from generate_options_keyboard import get_question
from quiz_index import get_quiz_index, update_quiz_index
from qustion import quiz_data

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Объект бота
bot = Bot(token="7500139640:AAEClpmSCWK0eyjIvVhMXwBhD10h-NvpNog")


# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    builder.add(types.KeyboardButton(text="Статистика"))
    await message.answer(
        "Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True)
    )


@dp.message(F.text == "Статистика")
async def show_statistics(message: types.Message):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            "SELECT result FROM quiz_results WHERE user_id = ?", (message.from_user.id,)
        ) as cursor:
            results = await cursor.fetchall()
            if results:
                last_result = results[-1][0]  # Получаем последний результат
                status_message = "Ваш последний результат: "
                status_message += "Успешно!" if last_result == 1 else "Неуспешно."
                await message.answer(status_message)
            else:
                await message.answer("Вы еще не проходили квиз.")


async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    await update_quiz_index(user_id, current_question_index)
    await get_question(message, user_id)


# Хэндлер на команду /quiz
@dp.message(F.text == "Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):

    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)


# Запуск процесса поллинга новых апдейтов
async def main():

    # Запускаем создание таблицы базы данных
    await create_table()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
