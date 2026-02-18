import os
import json
import numpy as np
from collections import Counter
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "history.json"

# ------------------ STORAGE ------------------

def load_history():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_history(history):
    with open(DATA_FILE, "w") as f:
        json.dump(history[-500:], f)

# ------------------ AI LOGIC ------------------

def predict_big_small(history):

    if len(history) < 20:
        return "BIG", 50.0, "LOW DATA"

    last200 = history[-200:]
    last15 = history[-15:]
    last5 = history[-5:]

    def to_bs(x):
        return "BIG" if x >= 5 else "SMALL"

    bs200 = [to_bs(x) for x in last200]
    bs15 = [to_bs(x) for x in last15]
    bs5 = [to_bs(x) for x in last5]

    p200 = Counter(bs200)
    p15 = Counter(bs15)
    p5 = Counter(bs5)

    big_score = (
        (p200["BIG"] / len(bs200)) * 0.4 +
        (p15["BIG"] / len(bs15)) * 0.35 +
        (p5["BIG"] / len(bs5)) * 0.25
    )

    prediction = "BIG" if big_score >= 0.5 else "SMALL"
    confidence = abs(big_score - 0.5) * 200

    std = np.std(last15)

    if std > 2.8:
        regime = "VOLATILE"
    elif std > 2:
        regime = "TREND"
    else:
        regime = "STABLE"

    return prediction, round(confidence, 2), regime

# ------------------ COMMANDS ------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ AI Prediction Bot Ready\nSend number or photo")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_history([])
    await update.message.reply_text("🔄 Data reset done")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history = load_history()
    await update.message.reply_text(f"📊 Stored Results: {len(history)}")

# ------------------ NUMBER INPUT ------------------

async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.strip()

    if not text.isdigit():
        return

    num = int(text)
    history = load_history()

    if history:
        last_pred = context.user_data.get("last_prediction")

        if last_pred:
            actual = "BIG" if num >= 5 else "SMALL"
            result = "WIN ✅" if actual == last_pred else "LOSS ❌"
            await update.message.reply_text(f"Result: {result}")

    history.append(num)
    save_history(history)

# ------------------ PHOTO INPUT ------------------

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    history = load_history()
    pred, conf, regime = predict_big_small(history)

    context.user_data["last_prediction"] = pred

    msg = f"""
📊 AI Market State: {regime}
🎯 Prediction: {pred}
🧠 Confidence: {conf}%
"""

    await update.message.reply_text(msg)

# ------------------ MAIN ------------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("status", status))

    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
