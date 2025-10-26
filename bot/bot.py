from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler
import os, asyncio

TOKEN = os.getenv("TOKEN")
BASE_URL = os.getenv("BASE_URL")
SELF_URL = os.getenv("SELF_URL")

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{SELF_URL}{WEBHOOK_PATH}"

app = Flask(__name__)

application = Application.builder().token(TOKEN).build()

async def start(update: Update, context):
    kb = [
        [InlineKeyboardButton("🎮 Играть в TON Miner", web_app={"url": f"{BASE_URL}/?ref={update.effective_user.id}"})]
    ]
    await update.message.reply_text("Запускай игру 👇", reply_markup=InlineKeyboardMarkup(kb))

application.add_handler(CommandHandler("start", start))

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok", 200

@app.route("/set_webhook")
def set_webhook():
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    new_loop.run_until_complete(application.bot.set_webhook(WEBHOOK_URL))
    new_loop.close()
    return f"Webhook установлен на {WEBHOOK_URL}", 200

@app.route("/")
def index():
    return "TON Miner Bot работает ✅", 200

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(application.initialize())
    loop.create_task(application.start())
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")))


