from app.database.init_db import criar_tabelas
from app.scheduler.scheduler import iniciar_scheduler


def main():
    # Idempotente: não recria tabelas que já existem.
    criar_tabelas()

    iniciar_scheduler()


if __name__ == "__main__":
    main()