import json
import numpy as np
import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

DATA_FILE = "data.json"

# ---------- DATA ----------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"history": [], "weights": {"trend": 0.5, "reversal": 0.3, "streak": 0.2}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# ---------- AI LOGIC ----------
def analyze(history, weights):
    if len(history) < 5:
        return None, 0

    last = history[-10:]
    big = sum(1 for x in last if x >= 5)
    small = len(last) - big

    trend_score = (big - small) / len(last)

    streak = 0
    for i in range(len(last)-1, 0, -1):
        if (last[i] >= 5) == (last[i-1] >= 5):
            streak += 1
        else:
            break

    reversal_score = -trend_score

    score = (
        trend_score * weights["trend"]
        + reversal_score * weights["reversal"]
        + (streak / 10) * weights["streak"]
    )

    prediction = "BIG" if score > 0 else "SMALL"
    confidence = round(abs(score) * 100, 2)

    return prediction, confidence

# ---------- COMMANDS ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 AI Bot Ready\nSend numbers then /predict")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    data["history"] = []
    save_data(data)
    await update.message.reply_text("🔄 Data reset done")

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    prediction, confidence = analyze(data["history"], data["weights"])

    if prediction is None:
        await update.message.reply_text("Data kam hai (min 5 results)")
        return

    context.user_data["last_prediction"] = prediction

    await update.message.reply_text(
        f"📊 Prediction: {prediction}\nConfidence: {confidence}%"
    )

# ---------- NUMBER INPUT ----------
async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not text.isdigit():
        await update.message.reply_text("Send number only")
        return

    num = int(text)

    data = load_data()
    data["history"].append(num)
    data["history"] = data["history"][-100:]

    if "last_prediction" in context.user_data:
        pred = context.user_data["last_prediction"]
        actual = "BIG" if num >= 5 else "SMALL"

        if pred == actual:
            result = "WIN ✅"
            data["weights"]["trend"] += 0.01
        else:
            result = "LOSS ❌"
            data["weights"]["trend"] -= 0.01

        save_data(data)
        await update.message.reply_text(f"Result: {result}")
    else:
        save_data(data)

# ---------- MAIN ----------
def main():
    TOKEN = os.getenv("BOT_TOKEN")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("predict", predict))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
