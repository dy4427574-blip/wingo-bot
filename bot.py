import os
from collections import deque
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

# Store last 200 results
history = deque(maxlen=200)

def big_small(num):
    return "BIG" if num >= 5 else "SMALL"

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 AI Prediction Bot Ready\n\n"
        "👉 Number bhejo (0-9)\n"
        "👉 Fir /predict dabao"
    )

# Save number
async def save_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        num = int(update.message.text)
        if 0 <= num <= 9:
            history.append(num)
            await update.message.reply_text(f"✅ Saved: {num}")
        else:
            await update.message.reply_text("❌ Send number 0-9")
    except:
        await update.message.reply_text("❌ Invalid number")

# Prediction logic
def predict_logic():
    if len(history) < 10:
        return "LOW DATA", "SMALL", 50

    last20 = list(history)[-20:]

    big_count = sum(1 for n in last20 if n >= 5)
    small_count = len(last20) - big_count

    trend = "BIG" if big_count > small_count else "SMALL"

    momentum = abs(big_count - small_count) / 20
    confidence = round(50 + momentum * 50, 1)

    return "ANALYZED", trend, confidence

# /predict
async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state, pred, conf = predict_logic()

    await update.message.reply_text(
        f"📊 AI Analysis: {state}\n"
        f"🎯 Prediction: {pred}\n"
        f"📈 Confidence: {conf}%"
    )

# /reset
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history.clear()
    await update.message.reply_text("🔄 History reset")

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
