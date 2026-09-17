from decimal import Decimal

from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models import HistoricoPreco, Produto
from app.scraper.factory import get_scraper_for_url


def cadastrar_produto(nome: str, url: str, preco_alvo: Decimal) -> Produto:
    """
    Cadastro simples, sem buscar dados do site — usado em scripts/testes
    manuais. Para a API/frontend, use `cadastrar_via_url`.
    """

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


def listar_produtos(session: Session) -> list[Produto]:
    return (
        session.query(Produto)
        .order_by(Produto.criado_em.desc())
        .all()
    )


def obter_produto(session: Session, produto_id: int) -> Produto | None:
    return session.get(Produto, produto_id)


def cadastrar_via_url(session: Session, url: str, preco_alvo: Decimal) -> Produto:
    """
    Cadastra um produto a partir apenas da URL: busca nome e preço atual
    automaticamente via scraper e já registra o primeiro ponto no histórico.
    """

    scraper = get_scraper_for_url(url)
    dados = scraper.get_product_data(url)

    preco_atual = Decimal(str(dados["preco"]))

    produto = Produto(
        nome=dados["nome"],
        url=dados["url"],
        preco_atual=preco_atual,
        preco_alvo=preco_alvo
    )
    session.add(produto)
    session.flush()  # garante produto.id antes de criar o histórico

    session.add(HistoricoPreco(produto_id=produto.id, preco=preco_atual))

    session.commit()
    session.refresh(produto)

    return produto


def atualizar_produto(
    session: Session,
    produto_id: int,
    preco_alvo: Decimal | None = None,
    ativo: bool | None = None
) -> Produto | None:

    produto = session.get(Produto, produto_id)

    if not produto:
        return None

    if preco_alvo is not None:
        produto.preco_alvo = preco_alvo

    if ativo is not None:
        produto.ativo = ativo

    session.commit()
    session.refresh(produto)

    return produto


def remover_produto(session: Session, produto_id: int) -> bool:

    produto = session.get(Produto, produto_id)

    if not produto:
        return False

    session.delete(produto)  # cascade apaga o histórico junto
    session.commit()

    return True


def obter_historico(session: Session, produto_id: int) -> list[HistoricoPreco]:
    return (
        session.query(HistoricoPreco)
        .filter(HistoricoPreco.produto_id == produto_id)
        .order_by(HistoricoPreco.coletado_em.asc())
        .all()
    )