import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

logging.basicConfig(level=logging.INFO)


class answers(StatesGroup):
    your_name = State()
    your_age = State()
    sum1 = State()
    sum2 = State()
    wonders = State()
    grey = State()


TOKEN = "700440860:AAFGbpZvobF0YxB37zw1092hfp8Bq7xB6zM"
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands = ['start', 'restart'], state = '*')
async def name(message: types.Message, state: FSMContext):
    async with state.proxy() as storage:
        storage["count_right_answers"] = 0
    await message.answer('Привет! Как тебя зовут?')
    await answers.your_name.set()


@dp.message_handler(state = answers.your_name)
async def age(message: types.Message, state: FSMContext):
    async with state.proxy() as storage:
        storage['name'] = message.text
    await message.answer(f'Рад знакомству! Сколько тебе лет, {storage["name"]}?')
    await answers.your_age.set()


@dp.message_handler(state = answers.your_age)
async def sum1(message: types.Message, state: FSMContext):
    async with state.proxy() as storage:
        storage['age'] = message.text
        keyboard_markup = types.ReplyKeyboardMarkup(row_width=3)
        keyboard_markup.add(types.KeyboardButton("12"),
                            types.KeyboardButton("16"),
                            types.KeyboardButton("15"),
                            types.KeyboardButton("20"))
        await message.answer("Давай начнем! Сколько будет 8 + 7?", reply_markup=keyboard_markup)
    await answers.sum1.set()


@dp.message_handler(state = answers.sum1)
async def sum2(message: types.Message, state: FSMContext):
    async with state.proxy() as storage:
        storage['sum1'] = message.text
        if message.text == "15":
            storage["count_right_answers"] += 1
        keyboard_markup = types.ReplyKeyboardMarkup(row_width=3, one_time_keyboard = True)
        keyboard_markup.add(types.KeyboardButton("50"),
                            types.KeyboardButton("56"),
                            types.KeyboardButton("44"),
                            types.KeyboardButton("68"))
        await message.answer("Сколько будет 8 * 7?", reply_markup= keyboard_markup)
        await answers.sum2.set()


@dp.message_handler(state = answers.sum2)
async def grey(message: types.Message, state: FSMContext):
    async with state.proxy() as storage:
        storage['sum2'] = message.text
        if message.text == "56":
            storage["count_right_answers"] += 1
    def get_keyboard():
        return types.InlineKeyboardMarkup().row(
                types.InlineKeyboardButton("50", callback_data = "50"),
                types.InlineKeyboardButton("77", callback_data = "77"),
                types.InlineKeyboardButton("58", callback_data = "58"),
                types.InlineKeyboardButton("1", callback_data = "1")
         )

    await message.answer("Сколько оттенков серого?", reply_markup=get_keyboard())
    await answers.grey.set()


@dp.callback_query_handler(state = answers.grey)
async def wonders(querry: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as storage:
        storage['grey'] = querry.data
        if querry.data == "50":
            storage["count_right_answers"] += 1
    def get_keyboard():
        return types.InlineKeyboardMarkup().row(
                types.InlineKeyboardButton("5", callback_data = "5"),
                types.InlineKeyboardButton("14", callback_data = "14"),
                types.InlineKeyboardButton("7", callback_data = "7"),
                types.InlineKeyboardButton("10", callback_data = "10")
         )
    await bot.send_message(querry.message.chat.id, "Сколько существует чудес света?", reply_markup=get_keyboard())
    await answers.wonders.set()
    await querry.answer()


@dp.callback_query_handler(state = answers.wonders)
async def results(querry: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as storage:
        if querry.data == "7":
            storage["count_right_answers"] += 1
        storage['wonders'] = querry.data
        wonders = storage["wonders"]
        name = storage["name"]
        age = storage["age"]
        sum1 = storage["sum1"]
        sum2 = storage["sum2"]
        grey = storage["grey"]
        right_answers = storage["count_right_answers"]
        await state.finish()
        await bot.send_message(querry.message.chat.id, f"Твое имя - {name}, твой возраст - {age}, твои ответы:"
                                                   f"\nПервый вопрос: {sum1}"
                                                   f"\nВторой вопрос: {sum2}"
                                                   f"\nТретий вопрос: {grey}"
                                                   f"\nЧетвертый вопрос: {wonders}"
                                                   f"\nВсего ты дал {right_answers} правильных ответов")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)