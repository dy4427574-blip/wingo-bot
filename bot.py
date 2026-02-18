import os
from collections import deque
import numpy as np
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

# store last results (max 50)
history = deque(maxlen=50)
last_predictions = deque(maxlen=5)

def big_small(num):
    return "BIG" if num >= 5 else "SMALL"

def ai_predict():
    if len(history) < 10:
        return None, 0

    last5 = list(history)[-5:]
    last10 = list(history)[-10:]
    last20 = list(history)[-20:]

    # convert to BIG SMALL
    bs10 = [big_small(x) for x in last10]
    bs5 = [big_small(x) for x in last5]

    trend_big = bs10.count("BIG")
    trend_small = bs10.count("SMALL")

    momentum = bs5[-1]
    momentum_boost = 2 if bs5.count(momentum) >= 3 else 0

    # reversal detection
    streak = 1
    for i in range(len(bs5)-1, 0, -1):
        if bs5[i] == bs5[i-1]:
            streak += 1
        else:
            break

    reversal = "BIG" if momentum == "SMALL" else "SMALL" if streak >= 4 else None

    score_big = trend_big
    score_small = trend_small

    if momentum == "BIG":
        score_big += momentum_boost
    else:
        score_small += momentum_boost

    if reversal == "BIG":
        score_big += 1
    elif reversal == "SMALL":
        score_small += 1

    if score_big > score_small:
        pred = "BIG"
        diff = score_big - score_small
    else:
        pred = "SMALL"
        diff = score_small - score_big

    confidence = min(78, 55 + diff * 5)

    return pred, confidence


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot ready\nSend number (0-9)")


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history.clear()
    last_predictions.clear()
    await update.message.reply_text("🔄 Data reset done")


async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pred, conf = ai_predict()
    if pred is None:
        await update.message.reply_text("Data kam hai (min 10)")
        return

    last_predictions.append(pred)
    await update.message.reply_text(f"📊 Prediction: {pred}\nConfidence: {conf:.1f}%")


async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("Send number only")
        return

    num = int(text)
    if num < 0 or num > 9:
        await update.message.reply_text("0-9 only")
        return

    history.append(num)

    if len(last_predictions) > 0:
        last_pred = last_predictions[-1]
        actual = big_small(num)

        if last_pred == actual:
            await update.message.reply_text("Result: WIN ✅")
        else:
            await update.message.reply_text("Result: LOSS ❌")


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("predict", predict))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number))

    app.run_polling()


if __name__ == "__main__":
    main()
