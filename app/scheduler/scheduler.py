import logging
import os
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

from app.services.price_checker import verificar_precos

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Intervalo entre verificações, em horas (configurável via .env)
INTERVALO_HORAS = float(os.getenv("CHECK_INTERVAL_HOURS", "6"))


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