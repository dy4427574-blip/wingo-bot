import os
import cv2
import numpy as np
import pytesseract
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

history = []
last_prediction = None

def big_small(num):
    return "BIG" if num >= 5 else "SMALL"

# RESET
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global history, last_prediction
    history = []
    last_prediction = None
    await update.message.reply_text("🔄 Data reset done")

# PHOTO ANALYSIS
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global history, last_prediction

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    file_path = "image.jpg"
    await file.download_to_drive(file_path)

    img = cv2.imread(file_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    text = pytesseract.image_to_string(gray)

    numbers = [int(x) for x in text if x.isdigit()]

    if len(numbers) < 5:
        await update.message.reply_text("❌ Data kam hai — clear photo bhejo")
        return

    history = numbers[-20:]

    big = sum(1 for n in history if n >= 5)
    small = len(history) - big

    prediction = "BIG" if big >= small else "SMALL"
    last_prediction = prediction

    await update.message.reply_text(
        f"📊 Numbers: {history[-10:]}\n"
        f"📈 BIG:{big} SMALL:{small}\n"
        f"🔮 Prediction: {prediction}"
    )

# NUMBER INPUT (WIN LOSS)
async def number_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global history, last_prediction

    try:
        num = int(update.message.text)
    except:
        await update.message.reply_text("Send number only")
        return

    history.append(num)
    result = big_small(num)

    if last_prediction:
        if result == last_prediction:
            status = "WIN ✅"
        else:
            status = "LOSS ❌"
    else:
        status = "No previous prediction"

    await update.message.reply_text(
        f"Added: {num}\nResult: {result}\nStatus: {status}"
    )

# START BOT
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("reset", reset))
app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, number_handler))

app.run_polling()
