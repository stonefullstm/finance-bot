from flask import Flask, request
from dotenv import load_dotenv
import asyncio
import os
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

app = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()


# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Seja bemvindo Finance Bot! Use /help para ver os comandos disponíveis."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Comandos disponíveis:\n"
        "/start - Iniciar o bot\n"
        "/help - Mostrar esta mensagem de ajuda\n"
        "/report - Gerar e enviar relatório financeiro\n"
    )
    await update.message.reply_text(help_text)

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
asyncio.get_event_loop().run_until_complete(application.initialize())
asyncio.get_event_loop().run_until_complete(application.start())


# Webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return "ok"


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=PORT)
