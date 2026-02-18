import asyncio
import numpy as np
from collections import deque
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

TOKEN = "YOUR_BOT_TOKEN"

# Store last 200 results
history = deque(maxlen=200)

last_prediction = None

def analyze():
    if len(history) < 5:
        return "LOW DATA", "BIG", 50.0

    arr = np.array(history)

    big = np.sum(arr >= 5)
    small = np.sum(arr < 5)

    trend_strength = abs(big - small) / len(arr)

    # Momentum (recent bias)
    recent = arr[-10:] if len(arr) >= 10 else arr
    momentum = (np.sum(recent >= 5) - np.sum(recent < 5)) / len(recent)

    # Randomness (std)
    volatility = np.std(arr) / 9

    score = (trend_strength * 0.4) + (momentum * 0.4) + ((1 - volatility) * 0.2)

    if momentum > 0:
        prediction = "BIG"
    else:
        prediction = "SMALL"

    confidence = 50 + (score * 50)
    confidence = round(max(50, min(confidence, 85)), 1)

    if trend_strength < 0.1:
        state = "RANDOM"
    elif trend_strength < 0.25:
        state = "NEUTRAL"
    else:
        state = "TREND"

    return state, prediction, confidence


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 AI Prediction Bot Ready\nSend number (0-9)")


async def save_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_prediction

    text = update.message.text.strip()

    if not text.isdigit():
        return

    num = int(text)
    history.append(num)

    # Check result if prediction existed
    if last_prediction:
        result = "WIN ✅" if (
            (last_prediction == "BIG" and num >= 5) or
            (last_prediction == "SMALL" and num < 5)
        ) else "LOSS ❌"

        await update.message.reply_text(f"Result: {result}")

    await update.message.reply_text(f"Saved: {num}")


async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_prediction

    msg = await update.message.reply_text("🔍 Analyzing market...")
    await asyncio.sleep(2.5)

    state, prediction, confidence = analyze()
    last_prediction = prediction

    text = (
        f"📊 Market State: {state}\n"
        f"🎯 Prediction: {prediction}\n"
        f"🧠 Confidence: {confidence}%\n"
        f"📦 Data Points: {len(history)}"
    )

    await msg.edit_text(text)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history.clear()
    await update.message.reply_text("♻️ Data reset done")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("predict", predict))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_number))

app.run_polling()
