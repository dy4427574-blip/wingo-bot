import os
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = os.getenv("BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

results = []
last_prediction = None

def start(update, context):
    update.message.reply_text("📸 Screenshot bhejo — bot auto analyse karega")

def extract_numbers_from_image(file_url):
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}"
    }

    data = {
        "model": "gpt-4.1-mini",
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Extract only visible numbers from this image as list"},
                    {"type": "input_image", "image_url": file_url}
                ]
            }
        ]
    }

    r = requests.post("https://api.openai.com/v1/responses", headers=headers, json=data)
    text = r.json()["output"][0]["content"][0]["text"]

    nums = []
    for t in text.replace(",", " ").split():
        if t.isdigit():
            n = int(t)
            if 0 <= n <= 9:
                nums.append(n)

    return nums

def photo_handler(update, context):
    global last_prediction

    photo = update.message.photo[-1]
    file = context.bot.getFile(photo.file_id)
    file_url = file.file_path

    nums = extract_numbers_from_image(file_url)

    if not nums:
        update.message.reply_text("Numbers detect nahi hue ❌")
        return

    results.extend(nums)

    if last_prediction:
        last = nums[-1]
        if (last >= 5 and last_prediction == "BIG") or (last < 5 and last_prediction == "SMALL"):
            update.message.reply_text("Result: WIN ✅")
        else:
            update.message.reply_text("Result: LOSS ❌")

    update.message.reply_text(f"Numbers detected ✅\n{nums}")

def predict(update, context):
    global last_prediction

    if len(results) < 10:
        update.message.reply_text("Data kam hai")
        return

    last5 = results[-5:]
    last15 = results[-15:] if len(results) >= 15 else results

    big5 = sum(1 for x in last5 if x >= 5)
    small5 = len(last5) - big5
    big15 = sum(1 for x in last15 if x >= 5)
    small15 = len(last15) - big15

    big_score = big5*2 + big15
    small_score = small5*2 + small15

    last_prediction = "BIG" if big_score > small_score else "SMALL"

    confidence = int(max(big_score, small_score)/(big_score+small_score)*100)

    update.message.reply_text(f"🔮 Prediction: {last_prediction}\nConfidence: {confidence}%")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("predict", predict))
    dp.add_handler(MessageHandler(Filters.photo, photo_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
