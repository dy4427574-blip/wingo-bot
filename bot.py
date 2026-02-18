import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = os.getenv("BOT_TOKEN")

results = []
last_prediction = None
wins = 0
losses = 0

def start(update, context):
    update.message.reply_text("Bot ready ✅ Send numbers")

def predict(update, context):
    global last_prediction

    if len(results) < 5:
        update.message.reply_text("Not enough data")
        return

    last7 = results[-7:]
    big = sum(1 for x in last7 if x >= 5)
    small = len(last7) - big

    if big > small:
        last_prediction = "SMALL"
    else:
        last_prediction = "BIG"

    update.message.reply_text(f"Prediction: {last_prediction}")

def stats(update, context):
    total = wins + losses
    acc = (wins / total * 100) if total > 0 else 0
    update.message.reply_text(
        f"Wins: {wins}\nLoss: {losses}\nAccuracy: {acc:.1f}%"
    )

def handle_number(update, context):
    global wins, losses, last_prediction

    try:
        num = int(update.message.text)
    except:
        update.message.reply_text("Send number only")
        return

    results.append(num)

    if len(results) > 50:
        results.pop(0)

    current = "BIG" if num >= 5 else "SMALL"

    msg = "Added"

    if last_prediction:
        if current == last_prediction:
            wins += 1
            msg += "\nResult: WIN ✅"
        else:
            losses += 1
            msg += "\nResult: LOSS ❌"

    update.message.reply_text(msg)

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("predict", predict))
dp.add_handler(CommandHandler("stats", stats))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_number))

updater.start_polling()
updater.idle()
