import os
import asyncio
from collections import deque
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

history = deque(maxlen=200)
last_prediction = None  # store BIG/SMALL

def big_small(num):
    return "BIG" if num >= 5 else "SMALL"

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 AI Prediction Bot Ready\n\n"
        "Send number (0-9)\n"
        "Then /predict"
    )

# SAVE NUMBER + RESULT CHECK
async def save_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_prediction

    try:
        num = int(update.message.text)
        if not (0 <= num <= 9):
            await update.message.reply_text("❌ Send 0-9 only")
            return

        history.append(num)

        result_type = big_small(num)

        if last_prediction:
            if last_prediction == result_type:
                await update.message.reply_text("✅ Result: WIN")
            else:
                await update.message.reply_text("❌ Result: LOSS")

            last_prediction = None

        await update.message.reply_text(f"💾 Saved: {num}")

    except:
        await update.message.reply_text("❌ Invalid")

# PREDICTION LOGIC
def predict_logic():
    if len(history) < 15:
        return "SMALL", 50.0

    last20 = list(history)[-20:]
    big_count = sum(1 for n in last20 if n >= 5)
    small_count = 20 - big_count

    pred = "BIG" if big_count > small_count else "SMALL"

    momentum = abs(big_count - small_count) / 20
    confidence = round(50 + momentum * 50, 1)

    return pred, confidence

# PREDICT
async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_prediction

    msg = await update.message.reply_text("🧠 AI analyzing data...")

    await asyncio.sleep(2.5)

    pred, conf = predict_logic()
    last_prediction = pred

    await msg.edit_text(
        f"📊 AI Analysis Complete\n"
        f"🎯 Prediction: {pred}\n"
        f"📈 Confidence: {conf}%"
    )

# RESET
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history.clear()
    await update.message.reply_text("🔄 History cleared")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("predict", predict))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, save_number))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
