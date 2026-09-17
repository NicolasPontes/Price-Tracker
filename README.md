# 📉 Notificador de Preço de Produtos

Aplicação web que monitora o preço de produtos em marketplaces online e avisa por e-mail assim que o preço cai — sem precisar ficar checando manualmente todos os dias.

Cole o link de um produto, defina o preço que você está disposto a pagar, e o sistema cuida do resto: verifica o preço periodicamente, guarda o histórico, e te manda um e-mail quando o preço cair.

## ✨ Funcionalidades

- 🔑 **Login multiusuário** — cada pessoa vê e gerencia só os próprios produtos, e recebe os alertas no próprio e-mail
- 🔎 **Cadastro automático** — cola só a URL do produto, o sistema busca nome e preço atual sozinho (não precisa digitar nada manualmente)
- ⏰ **Verificação periódica automática** — um agendador roda em background e reverifica os preços no intervalo configurado
- 📧 **Notificação por e-mail** — layout em HTML, com preço anterior, preço atual e % de desconto
- 📊 **Histórico de preços** — cada verificação fica registrada, com gráfico de evolução (sparkline) na interface
- ⏸️ **Pausar/retomar monitoramento** por produto, sem precisar excluir
- 🖱️ **Verificação manual sob demanda** — botão "Verificar agora" por produto, sem esperar o agendador

## 🏗️ Arquitetura

O projeto segue uma separação em camadas — a API, o agendador e os testes chamam a mesma camada de serviços, que por sua vez não sabe nada sobre HTTP nem sobre de onde a chamada está vindo:

```
app/
├── api/                  # Camada HTTP (FastAPI)
│   ├── main.py             # App principal: registra rotas, sobe o scheduler em background
│   ├── deps.py              # Dependências (sessão de banco, usuário autenticado via JWT)
│   ├── schemas.py           # Contratos de request/response (Pydantic)
│   └── routes/
│       ├── auth.py         # Registro e login
│       └── produtos.py     # CRUD de produtos monitorados
│
├── services/              # Regras de negócio (não sabe nada sobre HTTP)
│   ├── auth_service.py     # Registro/autenticação de usuário
│   ├── product_service.py  # CRUD de produtos, sempre escopado por dono
│   ├── price_checker.py    # Orquestra: roda o scraper, salva histórico, detecta queda
│   └── notification.py     # Monta e envia o e-mail de alerta
│
├── scraper/                # Um scraper por marketplace, atrás de uma interface comum
│   ├── base.py              # Interface ProductScraper (contrato)
│   ├── factory.py           # Escolhe o scraper certo pelo domínio da URL
│   └── mercado_livre.py     # Implementação para o Mercado Livre (via API oficial)
│
├── auth/                   # Autenticação e integrações externas
│   ├── security.py          # Hash de senha (bcrypt) e JWT
│   └── mercado_livre_auth.py # Fluxo OAuth2 com o Mercado Livre
│
├── database/
│   ├── models.py             # Usuario, Produto, HistoricoPreco (SQLAlchemy)
│   ├── connection.py         # Engine e sessão (SQL Server)
│   └── init_db.py             # Criação de tabelas
│
├── scheduler/
│   └── scheduler.py          # APScheduler: versão standalone e versão em background
│
└── frontend/                # Interface web (HTML/CSS/JS puro, sem framework)
    ├── index.html
    └── static/
        ├── style.css
        └── app.js
```

**Por que essa separação?** A camada `services/` é a mesma, seja quem estiver chamando: a API HTTP, o agendador rodando sozinho às 3h da manhã, ou um teste automatizado. Isso significa que adicionar um novo jeito de disparar uma verificação (ex: um comando de CLI, um webhook) não exige duplicar nenhuma regra de negócio.

## 🛠️ Tecnologias

| Camada | Tecnologia |
|---|---|
| Backend / API | Python, FastAPI |
| Banco de dados | SQL Server, SQLAlchemy (ORM) |
| Autenticação | JWT (`python-jose`) + hash de senha (`passlib`/`bcrypt`) |
| Agendamento | APScheduler |
| Frontend | HTML, CSS e JavaScript puro (sem framework) |
| Integração de dados | API oficial do Mercado Livre (OAuth2) |
| E-mail | SMTP (`smtplib`), HTML + texto |

## 🚀 Como rodar localmente

### Pré-requisitos

- Python 3.11+
- SQL Server (local ou remoto) com um banco de dados criado
- [ODBC Driver 18 for SQL Server](https://learn.microsoft.com/pt-br/sql/connect/odbc/download-odbc-driver-for-sql-server) instalado
- Uma conta de aplicação no [DevCenter do Mercado Livre](https://developers.mercadolivre.com.br/) (gratuita)
- Uma conta de e-mail com SMTP habilitado (ex: Gmail com "Senha de app")

### 1. Clonar e instalar dependências

```bash
git clone <url-do-seu-repositorio>
cd notificador-de-preco-de-produtos
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

Copie `.env.example` para `.env` e preencha com seus dados:

```bash
cp .env.example .env
```

| Variável | Descrição |
|---|---|
| `DB_SERVER`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_DRIVER` | Conexão com o SQL Server |
| `JWT_SECRET_KEY` | Chave para assinar os tokens de login. Gere com `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ML_APP_ID`, `ML_SECRET_KEY`, `ML_REDIRECT_URI` | Credenciais do seu app no DevCenter do Mercado Livre |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` | Conta que **envia** os e-mails de alerta |
| `CHECK_INTERVAL_HOURS` | De quantas em quantas horas os preços são reverificados |

### 3. Autorizar a integração com o Mercado Livre

Esse passo só precisa ser feito uma vez (o token se renova sozinho depois):

```bash
python -m app.auth.mercado_livre_auth
```

Siga as instruções no terminal: abrir a URL, autorizar o app, colar o código de volta.

### 4. Criar as tabelas do banco

```bash
python -m app.database.init_db
```

### 5. Subir a aplicação

```bash
uvicorn app.api.main:app --reload
```

Acesse:
- **Interface:** http://127.0.0.1:8000
- **Documentação interativa da API:** http://127.0.0.1:8000/docs

Ao abrir a interface pela primeira vez, crie uma conta — os produtos que você cadastrar ficam vinculados a ela, e os alertas de queda de preço vão para o e-mail dessa conta.

## 🧩 Decisões e desafios técnicos

Alguns pontos que valem destacar (e que geraram bastante aprendizado ao longo do projeto):

- **Scraping de HTML foi descartado a favor da API oficial.** A primeira versão usava `BeautifulSoup` direto no HTML da página, mas o Mercado Livre bloqueia requisições que "parecem bot", tornando a abordagem frágil e pouco confiável para um serviço que roda sem supervisão.
- **Nem todo `item_id` da URL é consultável diretamente.** IDs vindos de intervenções de carrinho/recomendação retornam `403` mesmo com token válido — a solução foi usar o `catalog_product_id` (o ID do produto "pai") com os endpoints `/products/{id}` e `/products/{id}/items`, que expõem a oferta em destaque (buy box) publicamente.
- **Refresh tokens OAuth2 são de uso único.** Cada renovação invalida o token anterior e gera um novo — o que exige salvar o par (access + refresh) a cada renovação, não só o access_token.
- **`IS 1` vs `= 1` no SQL Server.** SQLAlchemy traduz `.is_(True)` para `IS 1`, sintaxe rejeitada pelo T-SQL (que só aceita `IS` com `NULL`). A correção foi usar `== True` para gerar `= 1`.

## 🗺️ Roadmap

- [ ] Suporte a outros marketplaces (Amazon, eBay — avaliando viabilidade de API pública vs. scraping)
- [ ] Migrações de banco com Alembic (hoje as alterações de schema são aplicadas manualmente)
- [ ] Testes automatizados (pytest) para a camada de serviços
- [ ] Deploy público (Render/Railway) com link ao vivo

## 📄 Licença

Este projeto é de uso livre para fins de estudo e portfólio.