from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.auth import router as auth_router
from app.api.routes.produtos import router as produtos_router
from app.database.init_db import criar_tabelas
from app.scheduler.scheduler import iniciar_scheduler_background

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: garante que as tabelas existem e sobe o scheduler em background
    criar_tabelas()
    scheduler = iniciar_scheduler_background()

    yield

    # Shutdown: encerra o scheduler de forma limpa
    scheduler.shutdown()


app = FastAPI(
    title="Notificador de Preço de Produtos",
    lifespan=lifespan
)

app.include_router(auth_router)
app.include_router(produtos_router)

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR / "static"),
    name="static"
)


@app.get("/")
def index():
    return FileResponse(FRONTEND_DIR / "index.html")