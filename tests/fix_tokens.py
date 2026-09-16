import json
import time

# Cole aqui EXATAMENTE o JSON que veio no BODY do resultado do debug_refresh.py
tokens = {
    "access_token": "APP_USR-5608617907041786-091514-f44fad608efd32cfbc358b2617ed93c4-324441012",
    "token_type": "Bearer",
    "expires_in": 21600,
    "scope": "offline_access read urn:global:admin:info:/read-only urn:global:admin:info:/read-write urn:global:admin:oauth:/read-only urn:global:admin:oauth:/read-write urn:global:admin:users:/read-only urn:ml:all:comunication:/read-only urn:ml:all:publish-sync:/read-only urn:ml:mktp:ads:/read-only urn:ml:mktp:comunication:/read-only urn:ml:mktp:invoices:/read-only urn:ml:mktp:metrics:/read-only urn:ml:mktp:offers:/read-only urn:ml:mktp:orders-shipments:/read-only urn:ml:mktp:publish-sync:/read-only write",
    "user_id": 324441012,
    "refresh_token": "TG-6aa98e63d02e660001d2e4c7-324441012"
}

tokens["obtained_at"] = time.time()

with open("tokens.json", "w", encoding="utf-8") as f:
    json.dump(tokens, f, indent=2)

print("✅ tokens.json atualizado com o token válido mais recente!")