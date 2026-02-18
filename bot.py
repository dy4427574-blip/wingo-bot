import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

data = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot running ✅")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global data
    data = []
    await update.message.reply_text("Data reset ✅")

async def handle_numbers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global data
    
    text = update.message.text
    
    nums = [int(x) for x in text.split() if x.isdigit()]
    
    if not nums:
        await update.message.reply_text("Send number only")
        return
    
    data.extend(nums)
    data = data[-50:]
    
    await update.message.reply_text(f"Added {len(nums)} results ✅\nStored: {len(data)}")

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global data
    
    if len(data) < 15:
        await update.message.reply_text("Not enough data")
        return
    
    last7 = data[-7:]
    avg = sum(last7)/len(last7)
    
    result = "BIG" if avg >= 5 else "SMALL"
    
    await update.message.reply_text(f"Prediction: {result}")

app = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(CommandHandler("predict", predict))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_numbers))

app.run_polling()
