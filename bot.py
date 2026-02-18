import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.getenv("BOT_TOKEN")

data = []

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Bot ready ✅ Send numbers")

def reset(update: Update, context: CallbackContext):
    global data
    data = []
    update.message.reply_text("Data reset")

def predict(update: Update, context: CallbackContext):
    if len(data) < 5:
        update.message.reply_text("Not enough data")
        return

    last = data[-5:]
    avg = sum(last) / len(last)

    if avg >= 5:
        result = "BIG"
    else:
        result = "SMALL"

    update.message.reply_text(result)

def handle(update: Update, context: CallbackContext):
    try:
        num = int(update.message.text)
        data.append(num)
        update.message.reply_text("Added")
    except:
        update.message.reply_text("Send number only")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("predict", predict))
    dp.add_handler(CommandHandler("reset", reset))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
