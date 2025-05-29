import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from config import TOKEN
import json
import threading
import webserver

# بارگذاری درسنامه و تمرین‌ها
with open("lesson.json", encoding="utf-8") as f:
    LESSON_TEXT = json.load(f)["text"]

with open("exercises.json", encoding="utf-8") as f:
    EXERCISES = json.load(f)["questions"]

with open("quiz.json", encoding="utf-8") as f:
    QUIZ = json.load(f)["questions"]

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:
"
    keyboard += "📘 درسنامه
📝 تمرین
🧪 آزمون"
    await update.message.reply_text(keyboard)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if text == "📘 درسنامه":
        await update.message.reply_text(LESSON_TEXT)
    elif text == "📝 تمرین":
        user_data[user_id] = {"type": "exercise", "index": 0}
        question = EXERCISES[0]["question"]
        await update.message.reply_text(f"تمرین ۱:
{question}")
    elif text == "🧪 آزمون":
        user_data[user_id] = {"type": "quiz", "index": 0, "score": 0}
        question = QUIZ[0]["question"]
        await update.message.reply_text(f"آزمون ۱:
{question}")
    elif user_id in user_data:
        data = user_data[user_id]
        index = data["index"]

        if data["type"] == "exercise":
            answer = EXERCISES[index]["answer"]
            if text.strip() == answer:
                await update.message.reply_text("✅ درست بود!")
            else:
                await update.message.reply_text(f"❌ نادرست بود. جواب درست: {answer}")

            index += 1
            if index < len(EXERCISES):
                user_data[user_id]["index"] = index
                question = EXERCISES[index]["question"]
                await update.message.reply_text(f"تمرین {index+1}:
{question}")
            else:
                await update.message.reply_text("🎉 تمام تمرین‌ها تمام شدند.")
                del user_data[user_id]

        elif data["type"] == "quiz":
            answer = QUIZ[index]["answer"]
            if text.strip() == answer:
                user_data[user_id]["score"] += 1
                await update.message.reply_text("✅ درست بود!")
            else:
                await update.message.reply_text(f"❌ نادرست بود. جواب درست: {answer}")

            index += 1
            if index < len(QUIZ):
                user_data[user_id]["index"] = index
                question = QUIZ[index]["question"]
                await update.message.reply_text(f"سؤال {index+1}:
{question}")
            else:
                score = user_data[user_id]["score"]
                total = len(QUIZ)
                await update.message.reply_text(f"🌟 آزمون تمام شد! نمره‌ات: {score}/{total}")
                del user_data[user_id]
    else:
        await update.message.reply_text("دستور را متوجه نشدم. لطفاً یکی از گزینه‌ها را بفرستید.")

if __name__ == "__main__":
    threading.Thread(target=webserver.app.run, kwargs={"host": "0.0.0.0", "port": 8000}).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
