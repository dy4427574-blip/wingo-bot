import os
import asyncio
import numpy as np
from collections import deque
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

history = deque(maxlen=200)
last_prediction = None

def big_small(n):
    return 1 if n >= 5 else 0

def predict_logic():

    if len(history) < 10:
        return "LOW DATA", "BIG", 50

    arr = np.array([big_small(x) for x in history])

    long_term = np.mean(arr)
    short_term = np.mean(arr[-20:]) if len(arr) >= 20 else np.mean(arr)
    micro_term = np.mean(arr[-5:])

    score = (long_term * 0.4) + (short_term * 0.35) + (micro_term * 0.25)

    prediction = "BIG" if score >= 0.5 else "SMALL"
    confidence = abs(score - 0.5) * 200

    flips = np.sum(np.abs(np.diff(arr)))
    volatility = flips / len(arr)

    if volatility > 0.6:
        state = "RANDOM"
    elif volatility > 0.4:
        state = "NEUTRAL"
    else:
        state = "TREND"

    return state, prediction, round(confidence, 1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 AI Bot Ready\nSend numbers then /predict")

async def save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_prediction

    text = update.message.text.strip()
    if not text.isdigit():
        return

    num = int(text)
    history.append(num)

    if last_prediction:
        actual = "BIG" if num >= 5 else "SMALL"
        result = "WIN ✅" if actual == last_prediction else "LOSS ❌"
        await update.message.reply_text(f"Result: {result}")

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_prediction

    msg = await update.message.reply_text("🧠 Analyzing...")
    await asyncio.sleep(2.5)

    state, pred, conf = predict_logic()
    last_prediction = pred

    await msg.edit_text(
        f"📊 Market: {state}\n🎯 Prediction: {pred}\n📈 Confidence: {conf}%"
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("predict", predict))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save))

    app.run_polling()

if __name__ == "__main__":
    main()
