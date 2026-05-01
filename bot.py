import asyncio
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
    FSInputFile,
)
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

logging.basicConfig(level=logging.INFO)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
MINIAPP_URL = os.getenv("MINIAPP_URL")

# ✅ ЖБ id канала (ты получил через /pingchan)
CHANNEL_ID = -1003672493779

# ✅ твой user_id
OWNER_ID = 869398084

START_TEXT = (
    "👁 Добро пожаловать в Fantôme Boutique — курируемый бутик одежды.\n\n"
    "мы не продаём всё подряд.\n"
    "мы отбираем вещи и находим их для тебя.\n\n"
    "что внутри:\n\n"
    "• curated подбор — каждый айтем отобран вручную\n"
    "• витрина Fantôme — только актуальные и редкие вещи\n"
    "• персональный поиск — найдём вещь под твой запрос\n"
    "• избранное — сохраняй то, что откликнулось\n"
    "• чистый интерфейс — ничего лишнего, только вещи\n"
    "• прямой доступ — бутик всегда с тобой\n\n"
    "Fantôme — это не магазин.\n"
    "это пространство вещей, которые находят своих людей.\n\n"
    "открой бутик."
)

POST_TEXT = (
    "❕Добро пожаловать в Fantôme Boutique😭\n\n"
    "Fantôme Boutique  — Мы преследуем цели; качества, скорости, уверенности в товаре, для тебя!\n"
    "• Только проверенные поставщики\n"
    "• Контроль качества, брака перед отправкой (в ином случае, компенсация)\n"
    "• Честное описание товара\n"
    "• Отслеживание твоей посылки по твоему запросу\n\n"
    "О доставке : Доставка осуществляется БЕСПЛАТНО\n"
    "Приблизительные сроки: 🇰🇿🇷🇺 ± 14-21 дней\n\n"
    "Система бонусов : Не на количество, а на качество.\n\n"
    "Что мы предлагаем:\n"
    "• Реферальная система\n"
    "• Fantôme Level System\n"
    "• Mini-gifts\n\n"
    "Как сделать заказ? \n\n"
    "• Заходим в приложение\n"
    "• Добавляем товары в корзину\n"
    "• Нажимаем 'оформить заказ'\n"
    "• Бот сделает всё за тебя\n\n"
    "Если есть вопросы — менеджер "
)


def is_owner(m: Message) -> bool:
    return m.from_user is not None and m.from_user.id == OWNER_ID


# ✅ Кнопка ДЛЯ ЛИЧКИ: WebApp (мини-апп)
def kb_private_webapp() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text="Открыть",
            web_app=WebAppInfo(url=MINIAPP_URL)
        )
    ]])


# ✅ Кнопка ДЛЯ КАНАЛА: обычная ссылка (иначе BUTTON_TYPE_INVALID)
def kb_channel_link() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=" Открыть ",
            url=MINIAPP_URL
        )
    ]])


async def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не найден. Добавь BOT_TOKEN в Railway Variables.")
    if not MINIAPP_URL:
        raise ValueError("MINIAPP_URL не найден. Добавь MINIAPP_URL в Railway Variables.")

    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()

    # ✅ /start ДЛЯ ВСЕХ: картинка + текст + WebApp-кнопка
    @dp.message(CommandStart())
    async def start_handler(message: Message):
        try:
            photo = FSInputFile("start.png")  # файл должен быть рядом с bot.py
            await message.answer_photo(
                photo=photo,
                caption=START_TEXT,
                reply_markup=kb_private_webapp()
            )
        except Exception as e:
            logging.exception(f"Failed to send start photo: {e}")
            # если вдруг картинка не найдётся на сервере — отправим хотя бы текст
            await message.answer(START_TEXT, reply_markup=kb_private_webapp())

    # 🔐 /admin только тебе
    @dp.message(Command("admin"))
    async def admin_handler(message: Message):
        if not is_owner(message):
            return
        await message.answer(
            "Админ-команды:\n"
            "/pingchan — проверить канал и получить его ID\n"
            "/post — запостить в канал\n"
            "/postpin — пост + закреп (если у бота есть права)\n"
        )

    # 🔎 /pingchan: проверка канала (только тебе)
    @dp.message(Command("pingchan"))
    async def ping_channel(message: Message):
        if not is_owner(message):
            return
        try:
            chat = await bot.get_chat(CHANNEL_ID)
            await message.answer(
                "✅ Канал найден!\n"
                f"Название: {chat.title}\n"
                f"ID: {chat.id}\n"
                f"Username: @{chat.username if chat.username else 'нет'}"
            )
        except Exception as e:
            await message.answer(
                "❌ pingchan ошибка\n"
                f"CHANNEL_ID={CHANNEL_ID}\n"
                f"{type(e).__name__}: {e}"
            )

    # 🧾 /post: пост в канал (только тебе) — кнопка url
    @dp.message(Command("post"))
    async def post_to_channel(message: Message):
        if not is_owner(message):
            return

        try:
            photo = FSInputFile("fantom.jpg")

            msg = await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=photo,
                caption=POST_TEXT,
                reply_markup=kb_channel_link()
            )

            await message.answer(f"✅ Пост отправлен в канал\nmessage_id={msg.message_id}")

        except TelegramForbiddenError as e:
            await message.answer(
                "❌ Нет прав у бота писать в канал.\n"
                f"{type(e).__name__}: {e}"
            )

        except TelegramBadRequest as e:
            await message.answer(
                "❌ Telegram BadRequest.\n"
                f"{type(e).__name__}: {e}"
            )

        except Exception as e:
            await message.answer(f"❌ Ошибка: {type(e).__name__}: {e}")

    # 📌 /postpin: пост + закреп (только тебе)
    @dp.message(Command("postpin"))
    async def post_and_pin(message: Message):
        if not is_owner(message):
            return
        try:
            msg = await bot.send_message(
                chat_id=CHANNEL_ID,
                text=POST_TEXT,
                reply_markup=kb_channel_link(),
                disable_web_page_preview=True
            )
            await bot.pin_chat_message(
                chat_id=CHANNEL_ID,
                message_id=msg.message_id,
                disable_notification=True
            )
            await message.answer("✅ Запостил и закрепил")
        except TelegramForbiddenError as e:
            await message.answer(
                "❌ Нет прав на закреп или публикацию.\n"
                "Нужно: 'Публикация сообщений' и для закрепа: 'Закреплять сообщения'.\n\n"
                f"{type(e).__name__}: {e}"
            )
        except TelegramBadRequest as e:
            await message.answer(
                "❌ Telegram BadRequest.\n\n"
                f"CHANNEL_ID={CHANNEL_ID}\n"
                f"{type(e).__name__}: {e}"
            )
        except Exception as e:
            await message.answer(f"❌ Другая ошибка: {type(e).__name__}: {e}")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())