from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler
import os

TOKEN = os.getenv("TOKEN")
BASE_URL = os.getenv("BASE_URL")
WEBHOOK_URL = f"{BASE_URL}/webhook"

app = Flask(__name__)

telegram_app = Application.builder().token(TOKEN).build()

async def start(update: Update, context):
    kb = [[InlineKeyboardButton("🎮 Играть в TON Miner", web_app={"url": f"{BASE_URL}/?ref={update.effective_user.id}"})]]
    await update.message.reply_text("Запускай игру 👇", reply_markup=InlineKeyboardMarkup(kb))

telegram_app.add_handler(CommandHandler("start", start))

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.update_queue.put_nowait(update)
    return "ok"

@app.route("/set_webhook")
async def set_webhook():
    await telegram_app.bot.set_webhook(WEBHOOK_URL)
    return f"Webhook set to {WEBHOOK_URL}"

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.create_task(telegram_app.initialize())
    loop.create_task(telegram_app.start())
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")))

