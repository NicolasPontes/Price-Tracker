from decimal import Decimal

from app.database.connection import SessionLocal
from app.database.models import Produto

def cadastrar_produto(nome: str, url: str, preco_alvo: Decimal):
    with SessionLocal() as session:
        try:
            produto = Produto(nome=nome, url=url, preco_alvo=preco_alvo)
            session.add(produto)
            session.commit()
            session.refresh(produto)
            return produto
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()