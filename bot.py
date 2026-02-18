import os
import asyncio
from collections import deque
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN not found")

# last 200 numbers store
history = deque(maxlen=200)

last_prediction = None

def analyze():
    if len(history) < 5:
        return "SMALL", 50.0

    big = sum(1 for x in history if x >= 5)
    small = len(history) - big

    if big > small:
        confidence = (big / len(history)) * 100
        return "BIG", round(confidence, 1)
    else:
        confidence = (small / len(history)) * 100
        return "SMALL", round(confidence, 1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot Ready\nSend number (0-9) then /predict")

async def save_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_prediction

    try:
        num = int(update.message.text)
        if num < 0 or num > 9:
            return

        history.append(num)

        if last_prediction:
            predicted = last_prediction
            actual = "BIG" if num >= 5 else "SMALL"

            if predicted == actual:
                await update.message.reply_text("Result: WIN ✅")
            else:
                await update.message.reply_text("Result: LOSS ❌")

        await update.message.reply_text(f"✅ Saved: {num}")

    except:
        pass

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_prediction

    msg = await update.message.reply_text("🔎 Analyzing data...")
    await asyncio.sleep(2.5)

    prediction, confidence = analyze()
    last_prediction = prediction

    await msg.edit_text(
        f"📊 AI Analysis: DONE\n🎯 Prediction: {prediction}\n📈 Confidence: {confidence}%"
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("predict", predict))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_number))

    print("BOT RUNNING ✅")
    app.run_polling()

if __name__ == "__main__":
    main()
