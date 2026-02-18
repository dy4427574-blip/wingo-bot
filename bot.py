import os
import requests
from PIL import Image
from io import BytesIO
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler

TOKEN = os.getenv("BOT_TOKEN")

history = []
last_prediction = None

def analyze_trend(data):
    if len(data) < 5:
        return "SMALL", 50

    last5 = data[-5:]
    big = sum(1 for x in last5 if x >= 5)
    small = 5 - big

    if big > small:
        return "BIG", int((big/5)*100)
    else:
        return "SMALL", int((small/5)*100)

def start(update, context):
    update.message.reply_text("📸 Send screenshot")

def handle_photo(update, context):
    global last_prediction

    file = update.message.photo[-1].get_file()
    img = requests.get(file.file_path).content
    Image.open(BytesIO(img))  # placeholder processing

    pred, conf = analyze_trend(history)
    last_prediction = pred

    update.message.reply_text(
        f"📊 Prediction: {pred}\nConfidence: {conf}%"
    )

def handle_number(update, context):
    global last_prediction
    text = update.message.text.strip()

    if not text.isdigit():
        update.message.reply_text("Send number only")
        return

    num = int(text)
    history.append(num)

    if last_prediction:
        result = "WIN ✅" if (num >= 5 and last_prediction=="BIG") or (num < 5 and last_prediction=="SMALL") else "LOSS ❌"
        update.message.reply_text(f"Added\nResult: {result}")
    else:
        update.message.reply_text("Added")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_number))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
