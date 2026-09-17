import os
import smtplib
from decimal import Decimal
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

from app.database.models import Produto

load_dotenv()

# Estas variáveis são só a CONTA que ENVIA o e-mail (sua conta SMTP).
# O DESTINATÁRIO agora é sempre o e-mail do dono do produto (produto.usuario.email).
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def enviar_email_queda_preco(
    produto: Produto,
    preco_anterior: Decimal,
    preco_novo: Decimal
) -> None:
    """
    Envia um e-mail (texto + HTML) avisando que o preço de um produto caiu,
    para o e-mail cadastrado do dono do produto.
    """

    destinatario = produto.usuario.email

    if not all([SMTP_HOST, SMTP_USER, SMTP_PASSWORD, destinatario]):
        raise RuntimeError(
            "Configuração de e-mail incompleta. Defina SMTP_HOST, SMTP_USER "
            "e SMTP_PASSWORD no seu .env."
        )

    desconto_pct = (1 - (preco_novo / preco_anterior)) * 100

    assunto = f"📉 {produto.nome} caiu {desconto_pct:.0f}%!"

    corpo_texto = (
        f"O produto que você está monitorando teve uma queda de preço:\n\n"
        f"Produto: {produto.nome}\n"
        f"Preço anterior: R$ {preco_anterior:.2f}\n"
        f"Preço atual:    R$ {preco_novo:.2f}\n"
        f"Queda:          {desconto_pct:.1f}%\n\n"
        f"Link: {produto.url}\n"
    )

    corpo_html = f"""\
<html>
  <body style="margin:0;padding:0;background:#F6F3EC;font-family:Georgia,serif;color:#1C2620;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#F6F3EC;padding:32px 16px;">
      <tr>
        <td align="center">
          <table role="presentation" width="480" cellpadding="0" cellspacing="0" style="background:#FBF9F4;border:1px solid #DAD4C4;border-radius:4px;padding:32px;">
            <tr>
              <td style="font-size:12px;letter-spacing:0.04em;color:#6B6558;font-family:'Courier New',monospace;">
                QUEDA DE PREÇO DETECTADA
              </td>
            </tr>
            <tr>
              <td style="padding-top:10px;font-size:21px;font-weight:600;line-height:1.3;">
                {produto.nome}
              </td>
            </tr>
            <tr>
              <td style="padding-top:24px;">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="font-family:'Courier New',monospace;font-size:14px;">
                  <tr>
                    <td style="padding:5px 0;color:#6B6558;">Preço anterior</td>
                    <td style="padding:5px 0;text-align:right;text-decoration:line-through;color:#6B6558;">R$ {preco_anterior:.2f}</td>
                  </tr>
                  <tr>
                    <td style="padding:5px 0;color:#2F6B4F;font-weight:600;">Preço atual</td>
                    <td style="padding:5px 0;text-align:right;color:#2F6B4F;font-weight:600;font-size:19px;">R$ {preco_novo:.2f}</td>
                  </tr>
                  <tr>
                    <td style="padding:5px 0;color:#6B6558;">Queda</td>
                    <td style="padding:5px 0;text-align:right;color:#2F6B4F;">{desconto_pct:.1f}%</td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr>
              <td style="padding-top:28px;">
                <a href="{produto.url}" style="display:inline-block;background:#1C2620;color:#F6F3EC;text-decoration:none;padding:12px 22px;border-radius:3px;font-family:Georgia,serif;font-size:14px;">
                  Ver produto →
                </a>
              </td>
            </tr>
            <tr>
              <td style="padding-top:28px;font-size:11px;color:#6B6558;font-family:'Courier New',monospace;">
                Notificador de Preço de Produtos
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""

    mensagem = MIMEMultipart("alternative")
    mensagem["From"] = SMTP_USER
    mensagem["To"] = destinatario
    mensagem["Subject"] = assunto
    mensagem.attach(MIMEText(corpo_texto, "plain", "utf-8"))
    mensagem.attach(MIMEText(corpo_html, "html", "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(mensagem)