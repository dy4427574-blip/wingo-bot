import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

history = []
last_prediction = None
wins = 0
losses = 0

# ===== HELPER =====
def big_small(n):
    return "BIG" if n >= 5 else "SMALL"

def simple_predict(data):
    if len(data) < 5:
        return None, 0

    last5 = data[-5:]
    big_count = sum(1 for x in last5 if x >= 5)

    if big_count >= 3:
        pred = "BIG"
    else:
        pred = "SMALL"

    confidence = round((big_count / 5) * 100, 1)
    return pred, confidence

# ===== COMMANDS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot Ready\nSend number then /predict")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global history, wins, losses
    history = []
    wins = 0
    losses = 0
    await update.message.reply_text("🔄 Reset Done")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = wins + losses
    acc = (wins / total * 100) if total > 0 else 0
    await update.message.reply_text(
        f"📊 Total: {total}\n✅ Wins: {wins}\n❌ Loss: {losses}\n🎯 Accuracy: {acc:.1f}%"
    )

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_prediction

    pred, conf = simple_predict(history)

    if pred is None:
        await update.message.reply_text("❗ Send at least 5 numbers first")
        return

    last_prediction = pred
    await update.message.reply_text(f"🎯 Prediction: {pred}\n📉 Confidence: {conf}%")

# ===== NUMBER INPUT =====
async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global history, last_prediction, wins, losses

    text = update.message.text.strip()

    if not text.isdigit():
        await update.message.reply_text("Send number only")
        return

    num = int(text)
    history.append(num)

    if last_prediction:
        actual = big_small(num)

        if actual == last_prediction:
            wins += 1
            await update.message.reply_text("Result: WIN ✅")
        else:
            losses += 1
            await update.message.reply_text("Result: LOSS ❌")

# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("predict", predict))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number))

    print("BOT RUNNING...")
    app.run_polling()

if __name__ == "__main__":
    main()
