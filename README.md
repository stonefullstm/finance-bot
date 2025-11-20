# Finance Bot

É um Bot Telegram assistente financeiro usando IA. Ele registra transações numa planilha Google Sheets e fornece diagnóstico e insights com base nessas transações.
Aqui você encontrará os detalhes sobre o projeto: como instalar, executar, funcionalidades, recursos e tecnologias utilizadas.

## Introdução

O **Finance Bot** é uma aplicação que roda como um Bot no Telegram e por meio de comandos do usuário efetua lançamentos de receitas e despesas em uma planilha Google Sheets e usa IA para fazer um diagnóstico da situação financeira do usuário e fazer insights.

## Instalação e execução

1. Inicialmente, clone o repositório com o comando `git clone git@github.com:stonefullstm/finance-bot.git`
2. Crie um arquivo `.env` com base em `env.example`. Sendo necessário obter os tokens e demais informações de configuração constantes no arquivo.
3. O passo a passo para criar o projeto está disponível [neste artigo](https://professorcarlos.blogspot.com/2025/11/como-criar-um-bot-telegram-para-atualizar-planilha-financeira-Google-Sheets.html)
4. Na raiz do repositório clonado, execute:\
 `python -m venv .venv` para criar um ambiente virtual,\
 `.venv/Scripts/activate` para ativar o ambiente virtual e\
 `pip install -r requirements.txt` a fim de instalar as dependências
5. Execute `python finance_bot.py` para executar a aplicação

## Tecnologias utilizadas

Linguagem de programação [Pyhton](https://www.python.org/) e os pacotes [pandas](https://pandas.pydata.org/) e [python-telegram-bot](https://pypi.org/project/python-telegram-bot/), além de outras dependências presentes em `requirements.txt`.