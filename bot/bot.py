import os
import threading
from flask import Flask
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

# === Telegram bot ===
load_dotenv()
TOKEN = os.getenv("TOKEN")
BASE_URL = os.getenv("BASE_URL", "https://tonminer-2ybq.onrender.com")

app_bot = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("🎮 Играть в TON Miner",
          web_app=WebAppInfo(url=f"{BASE_URL}/?ref={update.effective_user.id}"))]]
    await update.message.reply_text("Запускай игру 👇", reply_markup=InlineKeyboardMarkup(kb))

app_bot.add_handler(CommandHandler("start", start))

def run_bot():
    print("🤖 Бот запущен...")
    app_bot.run_polling()

# === Flask keep-alive server ===
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "ok", 200

def run_flask():
    port = int(os.getenv("PORT", "10000"))
    print(f"🌐 Flask запущен на порту {port}")
    flask_app.run(host="0.0.0.0", port=port)

# === Запуск обоих потоков ===
if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    run_flask()



