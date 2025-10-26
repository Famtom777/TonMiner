import os, base64, hmac, hashlib, json
from urllib.parse import urlencode
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
BASE_URL = os.getenv("BASE_URL", "https://YOUR-WEBAPP.onrender.com")

if not TOKEN:
    raise RuntimeError("TOKEN required")

# (Опция) Если пока не внедрим initData-подпись, можно добавить ref-код к ссылке.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    qs = {"ref": u.id}  # чтобы новые могли подтянуть тебя как рефера
    url = f"{BASE_URL}/?{urlencode(qs)}"
    kb = [[InlineKeyboardButton("🎮 Играть", web_app=WebAppInfo(url=url))]]
    await update.message.reply_text("Запускай игру 👇", reply_markup=InlineKeyboardMarkup(kb))

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Команды: /start, /help")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    print("Bot running…")
    app.run_polling()

if __name__ == "__main__":
    main()
