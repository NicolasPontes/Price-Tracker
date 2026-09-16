import os
import smtplib
from decimal import Decimal
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

from app.database.models import Produto

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")


def enviar_email_queda_preco(
    produto: Produto,
    preco_anterior: Decimal,
    preco_novo: Decimal
) -> None:
    """
    Envia um e-mail avisando que o preço de um produto caiu.

    Requer as variáveis de ambiente (definidas no .env):
        SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_TO

    Funciona com Gmail (smtp.gmail.com, porta 587, com "senha de app"),
    Outlook (smtp.office365.com) ou qualquer outro provedor SMTP.
    """

    if not all([SMTP_HOST, SMTP_USER, SMTP_PASSWORD, EMAIL_TO]):
        raise RuntimeError(
            "Configuração de e-mail incompleta. Defina SMTP_HOST, SMTP_USER, "
            "SMTP_PASSWORD e EMAIL_TO no seu arquivo .env."
        )

    desconto_pct = (1 - (preco_novo / preco_anterior)) * 100

    assunto = f"📉 {produto.nome} caiu de preço!"

    corpo = (
        f"O produto que você está monitorando teve uma queda de preço:\n\n"
        f"Produto: {produto.nome}\n"
        f"Preço anterior: R$ {preco_anterior:.2f}\n"
        f"Preço atual:    R$ {preco_novo:.2f}\n"
        f"Queda:          {desconto_pct:.1f}%\n\n"
        f"Link: {produto.url}\n"
    )

    mensagem = MIMEMultipart()
    mensagem["From"] = SMTP_USER
    mensagem["To"] = EMAIL_TO
    mensagem["Subject"] = assunto
    mensagem.attach(MIMEText(corpo, "plain", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(mensagem)