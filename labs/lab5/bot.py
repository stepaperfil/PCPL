
import os
from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)


BOT_TOKEN = "здесь должен находиться токен"




async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    keyboard = [
        [KeyboardButton("🧮 Время"), KeyboardButton("📋 Меню")],
        [KeyboardButton("ℹ️ Помощь")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    text = (
        f"Привет, {user.first_name or 'друг'}! Я бот с кнопками.\n"
        "Выберите действие на клавиатуре или отправьте /menu"
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(
            "Доступные команды:\n"
            "/start — показать клавиатуру\n"
            "/menu — показать inline-кнопки\n"
            "/help — помощь\n\n"
            "Также можно нажимать кнопки на клавиатуре: '🧮 Время', '📋 Меню', 'ℹ️ Помощь'."
        )


async def menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Сказать привет 👋", callback_data="say_hello"),
            InlineKeyboardButton("Показать время 🕒", callback_data="show_time"),
        ],
        [
            InlineKeyboardButton("Счётчик +1 ➕", callback_data="counter_inc"),
            InlineKeyboardButton("Сбросить счётчик 🔁", callback_data="counter_reset"),
        ],
        [
            InlineKeyboardButton("Помощь ℹ️", callback_data="show_help"),
        ],
    ]
    if update.message:
        await update.message.reply_text(
            "Выберите действие:", reply_markup=InlineKeyboardMarkup(keyboard)
        )



async def handle_text_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    text = update.message.text.strip().lower()

    if "время" in text:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await update.message.reply_text(f"Текущее время: {now}")
    elif "меню" in text:
        await menu_cmd(update, context)
    elif "помощь" in text:
        await help_cmd(update, context)
    else:
        await update.message.reply_text("Не понял 🤔 Нажмите кнопку или команду /help")



async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()

    counter = context.user_data.get("counter", 0)

    if query.data == "say_hello":
        await query.edit_message_text("👋 Привет! Рада видеть тебя здесь.")
    elif query.data == "show_time":
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await query.edit_message_text(f"🕒 Сейчас: {now}")
    elif query.data == "counter_inc":
        counter += 1
        context.user_data["counter"] = counter
        await query.edit_message_text(f"Счётчик: {counter}\nНажмите ещё раз ➕")
    elif query.data == "counter_reset":
        context.user_data["counter"] = 0
        await query.edit_message_text("Счётчик сброшен до 0.")
    elif query.data == "show_help":
        await query.edit_message_text(
            "Inline-меню:\n"
            "• Сказать привет 👋\n"
            "• Показать время 🕒\n"
            "• Счётчик +1 ➕ / Сбросить счётчик 🔁"
        )
    else:
        await query.edit_message_text("Неизвестная команда.")


def main():
    if not BOT_TOKEN or "PASTE_YOUR_TELEGRAM_BOT_TOKEN_HERE" in BOT_TOKEN:
        raise RuntimeError(
            "Укажи токен бота: либо в переменной окружения BOT_TOKEN, "
            "либо в константе BOT_TOKEN в коде."
        )

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("menu", menu_cmd))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_buttons))

    app.add_handler(CallbackQueryHandler(on_callback))

    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    app.run_polling()


if __name__ == "__main__":
    main()
