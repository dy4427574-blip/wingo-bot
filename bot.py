import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

MAX_HISTORY = 200
history = []
last_prediction = None

def big_small(num):
    return "BIG" if num >= 5 else "SMALL"

def ai_predict():
    if len(history) < 20:
        return "Not enough data", 0

    last_200 = history[-200:]
    last_10 = history[-10:]

    big_count = sum(1 for n in last_200 if n >= 5)
    small_count = len(last_200) - big_count

    recent_big = sum(1 for n in last_10 if n >= 5)
    recent_small = 10 - recent_big

    momentum = recent_big - recent_small
    ratio = big_count - small_count

    score = (momentum * 0.6) + (ratio * 0.4)

    if score > 0:
        prediction = "BIG"
    else:
        prediction = "SMALL"

    confidence = min(90, abs(score) * 2)

    return prediction, round(confidence, 1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot ready ✅\nSend numbers or /predict")

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_prediction
    prediction, conf = ai_predict()

    if prediction == "Not enough data":
        await update.message.reply_text("Need at least 20 results")
        return

    last_prediction = prediction
    await update.message.reply_text(
        f"📊 AI Analysis\nPrediction: {prediction}\nConfidence: {conf}%"
    )

async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_prediction

    text = update.message.text.strip()
    if not text.isdigit():
        return

    num = int(text)
    history.append(num)

    if len(history) > MAX_HISTORY:
        history.pop(0)

    if last_prediction:
        result = big_small(num)
        if result == last_prediction:
            await update.message.reply_text("Result: WIN ✅")
        else:
            await update.message.reply_text("Result: LOSS ❌")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history.clear()
    await update.message.reply_text("History cleared")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("predict", predict))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number))

app.run_polling()
