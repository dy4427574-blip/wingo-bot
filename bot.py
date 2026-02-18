import os
from flask import Flask
from threading import Thread
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = os.getenv("BOT_TOKEN")

data = []

def start(update, context):
    update.message.reply_text("Bot running ✅")

def reset(update, context):
    global data
    data = []
    update.message.reply_text("Data reset ✅")

def predict(update, context):
    if len(data) < 5:
        update.message.reply_text("Not enough data")
        return

    last = data[-5:]
    avg = sum(last)/len(last)

    if avg >= 5:
        result = "BIG"
    else:
        result = "SMALL"

    update.message.reply_text(f"Prediction: {result}")

def add_number(update, context):
    try:
        num = int(update.message.text)
        data.append(num)
        if len(data) > 50:
            data.pop(0)

        update.message.reply_text(f"Added {num} ✅ Stored: {len(data)}")
    except:
        update.message.reply_text("Send number only")

def run_bot():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("reset", reset))
    dp.add_handler(CommandHandler("predict", predict))
    dp.add_handler(MessageHandler(Filters.text, add_number))

    updater.start_polling()
    updater.idle()

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot running"

def run():
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    Thread(target=run).start()
    run_bot()
