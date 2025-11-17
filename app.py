from flask import Flask, request
from dotenv import load_dotenv
import os
import asyncio
import logging
import threading
from datetime import date
from utils import (
    conectar_google_sheets,
    normalizar_string,
    validar_chat_id)
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    filters)


load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

app = Flask(__name__)
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Filtro customizado para validação de chat_id
class AuthorizedOnly(filters.BaseFilter):
    async def filter(self, update: Update) -> bool:
        return validar_chat_id(update.message.chat.id)


authorized_only = AuthorizedOnly()


# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        ("Seja bemvindo ao Finance Bot! "
         "Use /help para ver os comandos disponíveis.")
    )


async def help_command(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Comandos disponíveis:\n"
        "/start - Iniciar o bot\n"
        "/help - Mostrar esta mensagem de ajuda\n"
        "/save - Salvar um lançamento na planilha\n"
        "   /save valor/categoria/tipo/descrição (descrição é opcional)\n"
        "   Tipo deve ser 'Despesa' ou 'Receita'\n"
        "   Exemplo: /save 50,00/Alimentação/Despesa/Jantar com amigos\n"
        "/last - Mostrar as últimas 5 transações\n"
    )
    await update.message.reply_text(help_text)


async def save_command(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(
            ("Por favor, forneça informações a registrar separadas por /."
             "Digite no formato: valor/categoria/tipo/descrição."
             "Descrição é opcional."
             )
        )
        return
    dados = context.args[0].split("/")
    if len(dados) <= 3:
        await update.message.reply_text(
            ("Formato inválido. Use: valor/categoria/tipo/descrição"
             )
        )
        return
    valor = dados[0].replace(",", ".")
    try:
        float(valor)
    except ValueError:
        await update.message.reply_text(
            "O valor deve ser um número. Por favor, tente novamente."
        )
        return
    cliente = conectar_google_sheets()
    planilha = cliente.open("Minhas Finanças Pessoais")
    sheet = planilha.worksheet("Transações")
    sheet.append_row(
        [
            date.today().strftime("%d/%m/%Y"),
            dados[3] if len(dados) > 3 else "",
            normalizar_string(dados[1]).capitalize(),
            float(valor),
            normalizar_string(dados[2]).capitalize(),
        ]
    )
    await update.message.reply_text(
        f"""
        Você registrou: {dados[0]} para {dados[1]}
        no dia {date.today().strftime('%d/%m/%Y')}.
        """
    )


async def print_last_transactions(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cliente = conectar_google_sheets()
    planilha = cliente.open("Minhas Finanças Pessoais")
    sheet = planilha.worksheet("Transações")
    registros = sheet.get_all_records()
    ultimos = registros[-5:]  # Últimas 5 transações
    mensagem = "Últimas 5 transações:\n"
    for registro in ultimos:
        mensagem += (
            f"{registro['Data']}: {registro['Tipo']} de "
            f"{registro['Valor']} em {registro['Categoria']} - "
            f"{registro['Descrição']}\n"
        )
    await update.message.reply_text(mensagem)

application.add_handler(
    CommandHandler("start", start, filters=authorized_only))
application.add_handler(
    CommandHandler("help", help_command, filters=authorized_only))
application.add_handler(
    CommandHandler("save", save_command, filters=authorized_only))
application.add_handler(
    CommandHandler(
       "last", print_last_transactions, filters=authorized_only))

# asyncio.get_event_loop().run_until_complete(application.initialize())
# asyncio.get_event_loop().run_until_complete(application.start())
bot_loop = asyncio.new_event_loop()


def _run_loop():
    asyncio.set_event_loop(bot_loop)
    bot_loop.run_forever()


threading.Thread(target=_run_loop, daemon=True).start()

# Inicializa o application dentro do loop do bot (thread-safe)
asyncio.run_coroutine_threadsafe(application.initialize(), bot_loop).result()
asyncio.run_coroutine_threadsafe(application.start(), bot_loop).result()


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


# ---- Webhook ----
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        json_data = request.get_json(force=True)
        update = Update.de_json(json_data, application.bot)
        # asyncio.run(application.process_update(update))
        asyncio.run_coroutine_threadsafe(
            application.process_update(update), bot_loop)
        return "ok"
    except Exception as e:
        logger.error(f"Erro no webhook: {e}")
        return "erro", 500


if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=PORT)
