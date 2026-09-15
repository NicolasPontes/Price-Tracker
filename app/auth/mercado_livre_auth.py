"""
Autenticação OAuth2 com o Mercado Livre.

Fluxo (só precisa ser feito manualmente 1 vez):
1. Rode `python -m app.auth.mercado_livre_auth` -> ele imprime uma URL.
2. Abra a URL no navegador, faça login e autorize o app.
3. O ML vai te redirecionar para a REDIRECT_URI com um `?code=...` na URL.
4. Copie esse código e cole quando o script pedir.
5. O script troca o código por access_token + refresh_token e salva em
   `tokens.json` (não versionar esse arquivo!).

Depois disso, o resto do projeto (o scraper) só usa `get_valid_access_token()`,
que renova o token automaticamente quando ele expira.
"""

import json
import os
import time
import urllib.parse

import requests

TOKEN_URL = "https://api.mercadolibre.com/oauth/token"
AUTH_BASE_URL = "https://auth.mercadolivre.com.br/authorization"

# Ajuste esses 3 valores com o que você pegou no DevCenter,
# de preferência via variáveis de ambiente (não deixe hardcoded em produção).
APP_ID = os.environ.get("ML_APP_ID", "5608617907041786")
SECRET_KEY = os.environ.get("ML_SECRET_KEY", "oYx3hoDSlNdDOjgSlK0Ue0tLoFmgRdNH")
REDIRECT_URI = os.environ.get("ML_REDIRECT_URI", "https://tecaudio.vercel.app/")

TOKENS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "tokens.json"
)


def build_authorization_url() -> str:
    """Monta a URL que o usuário deve abrir no navegador para autorizar o app."""

    params = {
        "response_type": "code",
        "client_id": APP_ID,
        "redirect_uri": REDIRECT_URI,
    }

    return f"{AUTH_BASE_URL}?{urllib.parse.urlencode(params)}"


def exchange_code_for_token(authorization_code: str) -> dict:
    """Troca o código de autorização (obtido manualmente) por access_token + refresh_token."""

    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "client_id": APP_ID,
            "client_secret": SECRET_KEY,
            "code": authorization_code,
            "redirect_uri": REDIRECT_URI,
        },
        headers={"accept": "application/json"},
        timeout=15
    )

    response.raise_for_status()

    tokens = response.json()
    _salvar_tokens(tokens)

    return tokens


def refresh_access_token(refresh_token: str) -> dict:
    """Troca um refresh_token por um novo access_token (sem precisar do usuário logar de novo)."""

    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "client_id": APP_ID,
            "client_secret": SECRET_KEY,
            "refresh_token": refresh_token,
        },
        headers={"accept": "application/json"},
        timeout=15
    )

    response.raise_for_status()

    tokens = response.json()
    _salvar_tokens(tokens)

    return tokens


def get_valid_access_token() -> str:
    """
    Retorna um access_token válido, renovando automaticamente via refresh_token
    se o token salvo já estiver perto de expirar (ou expirado).

    Uso típico no scraper:
        token = get_valid_access_token()
        headers = {"Authorization": f"Bearer {token}"}
    """

    tokens = _carregar_tokens()

    if tokens is None:
        raise RuntimeError(
            "Nenhum token salvo. Rode `python -m app.auth.mercado_livre_auth` "
            "primeiro para autorizar o app."
        )

    # Margem de segurança de 5 minutos antes de considerar expirado
    expira_em = tokens["obtained_at"] + tokens["expires_in"] - 300

    if time.time() >= expira_em:
        tokens = refresh_access_token(tokens["refresh_token"])

    return tokens["access_token"]


def _salvar_tokens(tokens: dict) -> None:
    tokens["obtained_at"] = time.time()

    with open(TOKENS_FILE, "w", encoding="utf-8") as f:
        json.dump(tokens, f, indent=2)


def _carregar_tokens() -> dict | None:
    if not os.path.exists(TOKENS_FILE):
        return None

    with open(TOKENS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":

    if not APP_ID or not SECRET_KEY:
        print(
            "⚠️  Defina as variáveis de ambiente ML_APP_ID e ML_SECRET_KEY "
            "antes de rodar (ou edite os valores no topo deste arquivo)."
        )
        raise SystemExit(1)

    print("\n1) Abra esta URL no navegador e autorize o app:\n")
    print(build_authorization_url())
    print(
        "\n2) Depois de autorizar, você será redirecionado para algo como:\n"
        f"   {REDIRECT_URI}?code=TG-XXXXXXXXX...\n"
        "   (é normal a página dar erro de conexão, o importante é a URL)\n"
    )

    code = input("3) Cole aqui o valor do parâmetro 'code' da URL: ").strip()

    tokens = exchange_code_for_token(code)

    print("\n✅ Tokens salvos com sucesso em tokens.json!")
    print(f"   access_token expira em {tokens['expires_in']} segundos.")