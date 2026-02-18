import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = os.getenv("BOT_TOKEN")

results = []
last_prediction = None
last_outcome = None

# 🔹 START
def start(update, context):
    update.message.reply_text("Bot ready ✅ Send numbers")

# 🔹 ADD RESULT
def add_number(update, context):
    global last_outcome

    try:
        num = int(update.message.text)

        if num < 0 or num > 9:
            update.message.reply_text("Send number 0-9")
            return

        results.append(num)

        # check win loss
        if last_prediction:
            if (num >= 5 and last_prediction == "BIG") or (num < 5 and last_prediction == "SMALL"):
                last_outcome = "WIN ✅"
            else:
                last_outcome = "LOSS ❌"

            update.message.reply_text(f"Added\nResult: {last_outcome}")
        else:
            update.message.reply_text("Added")

    except:
        update.message.reply_text("Send number only")

# 🔹 PREDICT
def predict(update, context):
    global last_prediction

    if len(results) < 10:
        update.message.reply_text("Need at least 10 results")
        return

    last5 = results[-5:]
    last15 = results[-15:] if len(results) >= 15 else results

    big5 = sum(1 for x in last5 if x >= 5)
    small5 = len(last5) - big5

    big15 = sum(1 for x in last15 if x >= 5)
    small15 = len(last15) - big15

    big_score = (big5 * 2) + big15
    small_score = (small5 * 2) + small15

    # streak logic
    streak = results[-3:]

    if all(x >= 5 for x in streak):
        last_prediction = "SMALL"
        reason = "Big streak break"
    elif all(x < 5 for x in streak):
        last_prediction = "BIG"
        reason = "Small streak break"
    else:
        if big_score > small_score:
            last_prediction = "BIG"
            reason = "Trend"
        else:
            last_prediction = "SMALL"
            reason = "Trend"

    total = big_score + small_score
    confidence = int(max(big_score, small_score) / total * 100)

    update.message.reply_text(
        f"Prediction: {last_prediction}\nConfidence: {confidence}%\nMode: {reason}"
    )

# 🔹 STATUS
def status(update, context):
    total = len(results)
    if total == 0:
        update.message.reply_text("No data")
        return

    big = sum(1 for x in results if x >= 5)
    small = total - big

    update.message.reply_text(
        f"Total: {total}\nBig: {big}\nSmall: {small}"
    )

# 🔹 RESET
def reset(update, context):
    results.clear()
    update.message.reply_text("Data reset 🔄")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("predict", predict))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("reset", reset))

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, add_number))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
