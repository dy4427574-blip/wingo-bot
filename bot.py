import os
import requests
import pytesseract
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = os.getenv("BOT_TOKEN")

history = []
last_prediction = None

def extract_numbers(image_bytes):
    img = Image.open(BytesIO(image_bytes))
    img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(img)

    nums = [int(s) for s in text.split() if s.isdigit()]
    return nums

def analyze_trend(data):
    if len(data) < 5:
        return None, 0

    last5 = data[-5:]
    big = sum(1 for x in last5 if x >= 5)
    small = 5 - big

    if big > small:
        return "BIG", int((big/5)*100)
    else:
        return "SMALL", int((small/5)*100)

def start(update, context):
    update.message.reply_text("📸 Screenshot bhejo")

def handle_photo(update, context):
    global history, last_prediction

    file = update.message.photo[-1].get_file()
    img_bytes = requests.get(file.file_path).content

    nums = extract_numbers(img_bytes)

    if not nums:
        update.message.reply_text("❌ Numbers detect nahi hue")
        return

    history = nums[-20:]

    pred, conf = analyze_trend(history)

    if pred:
        last_prediction = pred
        update.message.reply_text(
            f"📊 Prediction: {pred}\nConfidence: {conf}%"
        )
    else:
        update.message.reply_text("Data kam hai")

def handle_number(update, context):
    global last_prediction
    text = update.message.text.strip()

    if not text.isdigit():
        update.message.reply_text("Number bhejo")
        return

    num = int(text)
    history.append(num)

    if last_prediction:
        if (num >= 5 and last_prediction=="BIG") or (num < 5 and last_prediction=="SMALL"):
            update.message.reply_text("Added\nResult: WIN ✅")
        else:
            update.message.reply_text("Added\nResult: LOSS ❌")
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
