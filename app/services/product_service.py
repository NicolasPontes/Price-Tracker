from decimal import Decimal

from sqlalchemy.orm import Session

from app.database.models import HistoricoPreco, Produto
from app.scraper.factory import get_scraper_for_url


def listar_produtos(session: Session, usuario_id: int) -> list[Produto]:
    return (
        session.query(Produto)
        .filter(Produto.usuario_id == usuario_id)
        .order_by(Produto.criado_em.desc())
        .all()
    )


def obter_produto(session: Session, produto_id: int, usuario_id: int) -> Produto | None:
    """
    Busca um produto garantindo que ele pertence ao usuário informado.
    Retorna None tanto se o produto não existe quanto se pertence a outro
    usuário — de propósito, pra não vazar pra terceiros se um ID existe ou não.
    """

    produto = session.get(Produto, produto_id)

    if produto is None or produto.usuario_id != usuario_id:
        return None

    return produto


def cadastrar_via_url(session: Session, usuario_id: int, url: str, preco_alvo: Decimal) -> Produto:
    """
    Cadastra um produto a partir apenas da URL: busca nome e preço atual
    automaticamente via scraper e já registra o primeiro ponto no histórico.
    """

    scraper = get_scraper_for_url(url)
    dados = scraper.get_product_data(url)

    preco_atual = Decimal(str(dados["preco"]))

    produto = Produto(
        usuario_id=usuario_id,
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
    usuario_id: int,
    preco_alvo: Decimal | None = None,
    ativo: bool | None = None
) -> Produto | None:

    produto = obter_produto(session, produto_id, usuario_id)

    if not produto:
        return None

    if preco_alvo is not None:
        produto.preco_alvo = preco_alvo

    if ativo is not None:
        produto.ativo = ativo

    session.commit()
    session.refresh(produto)

    return produto


def remover_produto(session: Session, produto_id: int, usuario_id: int) -> bool:

    produto = obter_produto(session, produto_id, usuario_id)

    if not produto:
        return False

    session.delete(produto)  # cascade apaga o histórico junto
    session.commit()

    return True


def obter_historico(session: Session, produto_id: int, usuario_id: int) -> list[HistoricoPreco] | None:

    produto = obter_produto(session, produto_id, usuario_id)

    if not produto:
        return None

    return (
        session.query(HistoricoPreco)
        .filter(HistoricoPreco.produto_id == produto_id)
        .order_by(HistoricoPreco.coletado_em.asc())
        .all()
    )