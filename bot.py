import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

# ===== DATA STORE =====
history = []
last_prediction = None
loss_streak = 0
wins = 0
losses = 0

# ===== UTIL =====
def big_small(n):
    return "BIG" if n >= 5 else "SMALL"

# ===== TREND ENGINE =====
def momentum_score(data):
    if len(data) < 5:
        return 0
    last = data[-5:]
    bigs = sum(1 for x in last if x >= 5)
    return bigs / 5

def volatility_score(data):
    if len(data) < 5:
        return 0
    flips = 0
    for i in range(1, len(data)):
        if big_small(data[i]) != big_small(data[i-1]):
            flips += 1
    return flips / len(data)

def streak_strength(data):
    if not data:
        return 0
    last = big_small(data[-1])
    streak = 1
    for i in range(len(data)-2, -1, -1):
        if big_small(data[i]) == last:
            streak += 1
        else:
            break
    return streak

# ===== REGIME =====
def detect_regime(data):
    if streak_strength(data) >= 3:
        return "TREND"
    if volatility_score(data) > 0.6:
        return "SIDEWAYS"
    return "NEUTRAL"

# ===== PREDICTION ENGINE =====
def make_prediction(data):
    global loss_streak

    regime = detect_regime(data)
    momentum = momentum_score(data)
    vol = volatility_score(data)
    streak = streak_strength(data)

    if regime == "TREND":
        pred = big_small(data[-1])

    elif regime == "SIDEWAYS":
        pred = "SMALL" if big_small(data[-1]) == "BIG" else "BIG"

    else:
        pred = "BIG" if momentum > 0.5 else "SMALL"

    if loss_streak >= 3:
        pred = "SMALL" if pred == "BIG" else "BIG"

    confidence = 50 + (streak * 3) + (momentum * 20) - (vol * 15)
    confidence = max(5, min(90, round(confidence, 1)))

    return pred, confidence, regime, momentum, vol

# ===== COMMANDS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 PRO AI BOT READY\nSend number or /predict")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global history, wins, losses, loss_streak
    history = []
    wins = 0
    losses = 0
    loss_streak = 0
    await update.message.reply_text("🔄 Data reset done")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total = wins + losses
    acc = (wins / total * 100) if total > 0 else 0
    await update.message.reply_text(
        f"📊 Total: {total}\n✅ Wins: {wins}\n❌ Loss: {losses}\n🎯 Accuracy: {acc:.1f}%\n⚠️ Loss streak: {loss_streak}"
    )

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_prediction

    if len(history) < 5:
        await update.message.reply_text("Data kam hai (min 5)")
        return

    pred, conf, regime, momentum, vol = make_prediction(history)
    last_prediction = pred

    msg = (
        f"📊 Regime: {regime}\n"
        f"📈 Momentum: {momentum:.2f}\n"
        f"🌪 Volatility: {vol:.2f}\n"
        f"🎯 Prediction: {pred}\n"
        f"📉 Confidence: {conf}%"
    )

    await update.message.reply_text(msg)

# ===== NUMBER INPUT =====
async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global history, last_prediction, wins, losses, loss_streak

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
            loss_streak = 0
            await update.message.reply_text("Result: WIN ✅")
        else:
            losses += 1
            loss_streak += 1
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
