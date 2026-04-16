import asyncio
import os
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
    FSInputFile,
)
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 פתח מערכת",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ]
        ]
    )

    caption = (
        "🛰️ *מערכת לוגיסטיקה 9950*\n"
        "━━━━━━━━━━━━━━━\n\n"

        "ברוך הבא למערכת ניהול המלאי של יחידה 9950.\n"
        "מערכת מתקדמת לניהול לוגיסטי חכם, מהיר ומדויק — ישירות מתוך טלגרם.\n\n"

        "⚙️ *מה המערכת מאפשרת:*\n"
        "• שליטה מלאה על מלאי מזון\n"
        "• מעקב אחר מחסור בזמן אמת\n"
        "• ניהול לפי מיקומים (מקררים / מחסן)\n"
        "• גיבוי ושחזור נתונים\n"
        "• יצוא דוחות Excel\n\n"

        "━━━━━━━━━━━━━━━\n\n"

        "👤 *כניסה רגילה*\n"
        "גישה לצפייה במצב המלאי:\n"
        "• בדיקת כמויות\n"
        "• זיהוי מחסור\n"
        "• צפייה בפעולות אחרונות\n\n"

        "🛠️ *כניסת מפתח*\n"
        "גישה לניהול מתקדם:\n"
        "• הוספה ומחיקה של מוצרים\n"
        "• עדכון כמויות\n"
        "• גיבוי ושליחת קבצים\n"
        "• טעינת נתונים מקובץ\n\n"

        "━━━━━━━━━━━━━━━\n\n"

        "🔐 לשימוש במצב מפתח נדרשת סיסמה\n\n"

        "🚀 *להתחלה לחץ על הכפתור למטה*"
    )

    # אם есть лого — отправляем как фото
    try:
        photo = FSInputFile("static/logo-9950.png")
        await message.answer_photo(
            photo=photo,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    except Exception:
        # если вдруг нет файла — просто текст
        await message.answer(
            caption,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    await message.answer(
        "שלום, לחץ על הכפתור כדי לפתוח את המחסן:",
        reply_markup=keyboard
    )


@dp.message()
async def fallback(message: Message):
    await message.answer("הבוט פעיל. פתח את המערכת דרך הכפתור /start")


async def main():
    print("Bot running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())