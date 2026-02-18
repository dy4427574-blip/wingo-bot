import os
import re
import logging
from collections import deque

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from openai import OpenAI

# ===== CONFIG =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(level=logging.INFO)

# Store last results
history = deque(maxlen=20)
last_prediction = None

# ===== HELPER =====
def big_small(num):
    return "BIG" if num >= 5 else "SMALL"

def analyze_trend(nums):
    big = sum(1 for n in nums if n >= 5)
    small = len(nums) - big
    return "BIG" if big > small else "SMALL"

# ===== COMMANDS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot ready\n\n📸 Send screenshot\nor\n🔢 Send number"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history.clear()
    global last_prediction
    last_prediction = None
    await update.message.reply_text("🔄 Data reset done")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not history:
        await update.message.reply_text("⚠️ No data yet")
        return

    trend = analyze_trend(list(history)[-10:])
    await update.message.reply_text(
        f"📊 Last {len(history)} results\nTrend: {trend}"
    )

# ===== NUMBER INPUT =====
async def number_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_prediction

    text = update.message.text.strip()

    if not text.isdigit():
        await update.message.reply_text("Send number only")
        return

    num = int(text)
    history.append(num)

    result = big_small(num)

    # Win/Loss check
    if last_prediction:
        if last_prediction == result:
            await update.message.reply_text("Result: WIN ✅")
        else:
            await update.message.reply_text("Result: LOSS ❌")

    # Make prediction
    if len(history) >= 5:
        prediction = analyze_trend(list(history)[-5:])
        last_prediction = prediction
        await update.message.reply_text(f"Prediction: {prediction}")
    else:
        await update.message.reply_text("Data added")

# ===== PHOTO HANDLER =====
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_prediction

    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_path = "image.jpg"
    await file.download_to_drive(file_path)

    with open(file_path, "rb") as img:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "Extract last visible numbers only"},
                        {"type": "input_image", "image": img},
                    ],
                }
            ],
        )

    text = response.output_text

    nums = list(map(int, re.findall(r"\d", text)))

    if not nums:
        await update.message.reply_text("❌ No numbers detected")
        return

    for n in nums:
        history.append(n)

    await update.message.reply_text(f"📥 Added {len(nums)} results")

    if len(history) >= 5:
        prediction = analyze_trend(list(history)[-5:])
        last_prediction = prediction
        await update.message.reply_text(f"Prediction: {prediction}")
    else:
        await update.message.reply_text("More data needed")

# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("status", status))

    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, number_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
