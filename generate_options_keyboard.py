import aiosqlite
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from db import DB_NAME, dp
from quiz_index import get_quiz_index, update_quiz_index
from qustion import quiz_data


def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(
            types.InlineKeyboardButton(
                text=option,
                callback_data=(
                    "right_answer" if option == right_answer else "wrong_answer"
                ),
            )
        )

    builder.adjust(1)
    return builder.as_markup()


@dp.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    # Получаем текст ответа пользователя
    user_answer = callback.message.reply_markup.inline_keyboard[0][0].text

    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None,
    )

    await callback.message.answer(f"Верно! Ваш ответ: {user_answer}")

    current_question_index = await get_quiz_index(callback.from_user.id)
    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await save_result(callback.from_user.id, True)
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")


@dp.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    # Получаем текст ответа пользователя
    user_answer = callback.message.reply_markup.inline_keyboard[0][0].text

    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None,
    )

    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]["correct_option"]

    await callback.message.answer(
        f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}. Ваш ответ: {user_answer}"
    )

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await save_result(callback.from_user.id, False)
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")


async def get_question(message, user_id):

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]["correct_option"]
    opts = quiz_data[current_question_index]["options"]
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(
        f"{quiz_data[current_question_index]['question']}", reply_markup=kb
    )


async def save_result(user_id, is_successful):
    async with aiosqlite.connect(DB_NAME) as db:
        result_status = (
            1 if is_successful else 0
        )  # 1 - успешный результат, 0 - неуспешный результат
        await db.execute(
            "INSERT OR REPLACE INTO quiz_results (user_id, result) VALUES (?, ?)",
            (user_id, result_status),
        )
        await db.commit()
