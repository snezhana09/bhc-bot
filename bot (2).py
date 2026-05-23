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
BOT_TOKEN  = "8922098628:AAE5gq7vfarfC5S0W4FdX1agwIi83ZpIdjo"
PDF_PATH   = "guide.pdf"
CSV_FILE   = "clients.csv"
ADMIN_USERNAME = "snmgk0"
# ─────────────────────────────────────────

ASK_NICHE = 1
ASK_CUSTOM = 2

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)

NICHES = [
    ["SMM", "Владелец бизнеса"],
    ["Маркетолог / Креативный директор", "Управляющий / СЕО"],
    ["Другое"],
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


async def send_guide(update: Update, niche: str):
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
            caption="«25 активаций к лету для бизнеса» от Brand Health Clinic 🌿\n\nХотите разработать активацию или экспресс-стратегию под ваш бренд? Пишите в директ @bhc_buro или в тг @bhcaccount 💬",
            read_timeout=120,
            write_timeout=120,
            connect_timeout=60,
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(NICHES, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! 👋 Я бот Brand Health Clinic.\n\n"
        "Сейчас отправлю вам гайд «25 активаций к лету для бизнеса» 🎁\n\n"
        "Скажите, чем вы занимаетесь?",
        reply_markup=keyboard
    )
    return ASK_NICHE


async def ask_niche(update: Update, context: ContextTypes.DEFAULT_TYPE):
    niche = update.message.text

    if niche == "Другое":
        await update.message.reply_text(
            "Напишите, чем вы занимаетесь 👇",
            reply_markup=ReplyKeyboardRemove()
        )
        return ASK_CUSTOM

    await send_guide(update, niche)
    return ConversationHandler.END


async def ask_custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    niche = update.message.text
    await send_guide(update, niche)
    return ConversationHandler.END


async def clients(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.username != ADMIN_USERNAME:
        await update.message.reply_text("⛔ У тебя нет доступа к этой команде.")
        return

    if not os.path.isfile(CSV_FILE):
        await update.message.reply_text("Пока нет ни одного клиента.")
        return

    with open(CSV_FILE, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    if len(rows) <= 1:
        await update.message.reply_text("Пока нет ни одного клиента.")
        return

    text = "📋 *Список клиентов:*\n\n"
    for row in rows[1:]:
        date, uid, username, name, niche = row
        text += f"👤 {name} {username}\n🗂 {niche} | 📅 {date}\n\n"

    if len(text) > 4000:
        text = text[:4000] + "\n\n...список обрезан."

    await update.message.reply_text(text, parse_mode="Markdown")


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Напишите /start чтобы начать 😊")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NICHE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_niche)],
            ASK_CUSTOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_custom)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("clients", clients))
    logging.info("🤖 Бот запущен...")
    app.run_polling(close_loop=False)


if __name__ == "__main__":
    main()
