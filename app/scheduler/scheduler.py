import logging
import os
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

from app.services.price_checker import verificar_precos

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)

# Intervalo entre verificações, em horas (configurável via .env)
INTERVALO_HORAS = float(os.getenv("CHECK_INTERVAL_HOURS", "6"))


def iniciar_scheduler_background() -> BackgroundScheduler:
    """
    Versão não-bloqueante do scheduler, para rodar dentro do mesmo processo
    da API (FastAPI): não trava a thread principal, então o servidor web
    continua respondendo requisições normalmente.
    """

    scheduler = BackgroundScheduler()

    scheduler.add_job(
        verificar_precos,
        trigger="interval",
        hours=INTERVALO_HORAS,
        next_run_time=datetime.now(),
        id="verificar_precos"
    )

    scheduler.start()
    logger.info(
        "⏰ Scheduler (background) iniciado. Verificando preços a cada %sh.",
        INTERVALO_HORAS
    )

    return scheduler


def iniciar_scheduler() -> None:
    """
    Inicia o scheduler que roda `verificar_precos()` a cada
    `CHECK_INTERVAL_HOURS` horas, começando imediatamente na primeira vez.
    """

    scheduler = BlockingScheduler()

    scheduler.add_job(
        verificar_precos,
        trigger="interval",
        hours=INTERVALO_HORAS,
        next_run_time=datetime.now(),  # roda uma vez imediatamente ao iniciar
        id="verificar_precos"
    )

    print(f"⏰ Scheduler iniciado. Verificando preços a cada {INTERVALO_HORAS}h.")
    print("   Pressione Ctrl+C para encerrar.\n")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n👋 Scheduler encerrado.")