import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

# Загружаем токен и ID администратора из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # ID группы или админа в Telegram

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Главное меню
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Записаться на консультацию")],
        [KeyboardButton(text="❓ Задать вопрос")],
        [KeyboardButton(text="ℹ️ О нас")]
    ],
    resize_keyboard=True
)

# --- Машина состояний для анкеты ---
class ConsultationForm(StatesGroup):
    name = State()
    country = State()
    program = State()
    contact = State()

# --- FSM для вопросов ---
class QuestionForm(StatesGroup):
    waiting = State()

# --- Команда /start ---
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    text = (
        "👋 Привет! Я — бот агентства *China is Calling* 🇨🇳\n\n"
        "Мы помогаем абитуриентам поступить в университеты Китая:\n"
        "🎓 Подбор программ и университетов\n"
        "📝 Помощь с документами и консультация по визам\n"
        "🏙️ Поддержка после приезда\n\n"
        "Выбери, что тебя интересует 👇"
    )
    await message.answer(text, reply_markup=menu, parse_mode="Markdown")

# --- АНКЕТА ---
@dp.message(F.text == "📅 Записаться на консультацию")
async def start_form(message: types.Message, state: FSMContext):
    await message.answer("Давай начнём! 😊\n\nКак тебя зовут?", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ConsultationForm.name)

@dp.message(ConsultationForm.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Отлично! 🌍 Из какой ты страны?")
    await state.set_state(ConsultationForm.country)

@dp.message(ConsultationForm.country)
async def get_country(message: types.Message, state: FSMContext):
    await state.update_data(country=message.text)
    await message.answer("Какую программу ты рассматриваешь? (например: бакалавриат, магистратура, языковые курсы)")
    await state.set_state(ConsultationForm.program)

@dp.message(ConsultationForm.program)
async def get_program(message: types.Message, state: FSMContext):
    await state.update_data(program=message.text)
    await message.answer("📞 Укажи, как с тобой связаться (Telegram @username, телефон или email):")
    await state.set_state(ConsultationForm.contact)

@dp.message(ConsultationForm.contact)
async def finish_form(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    data = await state.get_data()

    text = (
        f"📝 *Новая заявка на консультацию!*\n\n"
        f"👤 Имя: {data['name']}\n"
        f"🌍 Страна: {data['country']}\n"
        f"🎓 Программа: {data['program']}\n"
        f"📞 Контакт: {data['contact']}\n"
    )

    # Отправляем админу/группе
    try:
        await bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
    except Exception:
        pass

    # Подтверждение пользователю
    await message.answer(
        "Спасибо! 🙌\nТвоя заявка отправлена менеджеру. Мы скоро с тобой свяжемся 💬",
        reply_markup=menu
    )
    await state.clear()

# --- О НАС ---
@dp.message(F.text == "ℹ️ О нас")
async def about_handler(message: types.Message):
    await message.answer(
        "🏫 *О нас*\n\n"
        "Мы — агентство *China is Calling*, помогаем студентам поступить в университеты Китая 🇨🇳.\n\n"
        "Наши услуги:\n"
        "• Подбор университетов и программ\n"
        "• Помощь с поступлением и визой\n"
        "• Поддержка студентов в Китае\n\n"
        "Связаться с нами:\n"
        "🌐 Сайт: @щас будет\n"
        "💬 Telegram: @делаем\n"
        "📸 Instagram: [china.is.calling](https://www.instagram.com/china.is.calling)\n"
        "📺 YouTube: [China is Calling](https://youtube.com/@chinaiscalling)\n"
        "📢 Канал: [t.me/chinaiscalling](https://t.me/chinaiscalling)\n"
        "🎵 TikTok: [china.is.calling](https://www.tiktok.com/@china.is.calling?_t=ZT-90rwJj7bEYo&_r=1)\n"
        "🅱️ VK: [china.is.calling](https://vk.com/club233354704)",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

# --- ВОПРОСЫ ---
@dp.message(F.text == "❓ Задать вопрос")
async def question_handler(message: types.Message, state: FSMContext):
    await state.set_state(QuestionForm.waiting)  # временное состояние для вопросов
    await message.answer(
        "💬 Напиши свой вопрос сюда, и мы ответим в ближайшее время."
    )

@dp.message(QuestionForm.waiting)
async def handle_user_question(message: types.Message, state: FSMContext):
    user = message.from_user
    question = message.text

    # Отправка админу/в группу
    try:
        await bot.send_message(
            ADMIN_ID,
            f"📩 *Новый вопрос от* [{user.full_name}](tg://user?id={user.id}):\n\n{question}",
            parse_mode="Markdown"
        )
    except Exception:
        pass

    # Ответ пользователю
    await message.answer(
        "✅ Спасибо! Мы получили твой вопрос и скоро с тобой свяжемся 🙌",
        reply_markup=menu
    )

    await state.clear()

# --- Запуск ---
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
