from dotenv import load_dotenv
import os
import logging
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
    # Verifica se o usuário forneceu argumentos
    if not context.args:
        await update.message.reply_text(
            ("Por favor, forneça informações a registrar separadas por /."
             "Digite no formato: valor/categoria/tipo/descrição."
             "Descrição é opcional."
             )
        )
        return
    # Obtém os dados fornecidos pelo usuário e separa-os
    dados = context.args[0].split("/")
    # Verifica se há pelo menos 3 partes (valor, categoria, tipo)
    if len(dados) <= 3:
        await update.message.reply_text(
            ("Formato inválido. Use: valor/categoria/tipo/descrição"
             )
        )
        return
    # Valida o valor fornecido
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
    # Adiciona uma nova linha na planilha com os dados fornecidos
    sheet.append_row(
        [
            date.today().strftime("%d/%m/%Y"),
            dados[3] if len(dados) > 3 else "",
            normalizar_string(dados[1]).capitalize(),
            float(valor),
            normalizar_string(dados[2]).capitalize(),
        ]
    )
    # Dá feedback ao usuário
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


def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("Defina as variáveis de ambiente TELEGRAM_TOKEN.")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(
        CommandHandler("start", start, filters=authorized_only))
    app.add_handler(
        CommandHandler("help", help_command, filters=authorized_only))
    app.add_handler(
        CommandHandler("save", save_command, filters=authorized_only))
    app.add_handler(
        CommandHandler(
            "last", print_last_transactions, filters=authorized_only))

    logger.info("Bot iniciado.")
    app.run_polling()


if __name__ == "__main__":
    main()
