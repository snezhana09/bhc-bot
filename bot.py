import logging
import csv
import os
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# ─────────────────────────────────────────
BOT_TOKEN = "8922098628:AAE5gq7vfarfC5S0W4FdX1agwIi83ZpIdjo"
PDF_PATH  = "guide.pdf"
CSV_FILE  = "clients.csv"
# ─────────────────────────────────────────

ASK_NICHE = 1

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)

NICHES = [
    ["SMM", "Маркетолог / Креативный директор"],
    ["Владелец бизнеса", "Фаундер"],
    ["PR-специалист", "Управляющий / СЕО"],
]


def save_client(user, niche):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Дата", "ID", "Username", "Имя", "Ниша"])
        writer.writerow([
            datetime.now().strftime("%d.%m.%Y %H:%M"),
            user.id,
            f"@{user.username}" if user.username else "—",
            user.full_name,
            niche
        ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(NICHES, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! 👋 Я бот Brand Health Clinic.\n\n"
        "Сейчас отправлю тебе гайд «25 активаций к лету для бизнеса» 🎁\n\n"
        "Скажи, кто ты по роду деятельности?",
        reply_markup=keyboard
    )
    return ASK_NICHE


async def ask_niche(update: Update, context: ContextTypes.DEFAULT_TYPE):
    niche = update.message.text
    user = update.effective_user

    save_client(user, niche)
    logging.info(f"✅ Новый клиент: {user.full_name} (@{user.username}), ниша: {niche}")

    await update.message.reply_text(
        "Отлично! 🔥 Отправляю файл... ⏳",
        reply_markup=ReplyKeyboardRemove()
    )

    with open(PDF_PATH, "rb") as pdf_file:
        await update.message.reply_document(
            document=pdf_file,
            caption="«25 активаций к лету для бизнеса» от Brand Health Clinic 🌿\n\nХочешь разработать активацию или экспресс-стратегию под свой бренд? Пиши в директ @bhc_buro или в тг @bhcaccount 💬",
            read_timeout=120,
            write_timeout=120,
            connect_timeout=60,
        )

    return ConversationHandler.END


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Напиши /start чтобы начать 😊")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NICHE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_niche)],
        },
        fallbacks=[MessageHandler(filters.ALL, fallback)],
    )

    app.add_handler(conv)
    logging.info("🤖 Бот запущен...")
    app.run_polling(close_loop=False)


if __name__ == "__main__":
    main()
