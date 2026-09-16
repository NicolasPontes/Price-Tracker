import logging
from decimal import Decimal

from app.database.connection import SessionLocal
from app.database.models import HistoricoPreco, Produto
from app.scraper.factory import get_scraper_for_url
from app.services.notification import enviar_email_queda_preco

logger = logging.getLogger(__name__)


def verificar_precos() -> None:
    """
    Percorre todos os produtos ativos cadastrados no banco, busca o preço
    atual de cada um via scraper, salva no histórico e dispara notificação
    por e-mail se o preço caiu em relação à última verificação.

    Ponto de entrada chamado periodicamente pelo scheduler.
    """

    with SessionLocal() as session:
        produtos = (
            session.query(Produto)
            .filter(Produto.ativo == True)  # noqa: E712 - "== True" gera "= 1", compatível com SQL Server; ".is_(True)" gera "IS 1", que o T-SQL rejeita
            .all()
        )

        logger.info("Verificando preços de %d produto(s) ativo(s)...", len(produtos))

        for produto in produtos:
            try:
                _verificar_produto(session, produto)
            except Exception:
                # Um produto com erro (ex: site fora do ar, item removido)
                # não deve travar a verificação dos outros produtos.
                logger.exception(
                    "Erro ao verificar produto '%s' (id=%s)", produto.nome, produto.id
                )
                session.rollback()
                continue


def _verificar_produto(session, produto: Produto) -> None:

    scraper = get_scraper_for_url(produto.url)
    dados = scraper.get_product_data(produto.url)

    preco_novo = Decimal(str(dados["preco"]))
    preco_anterior = produto.preco_atual

    session.add(HistoricoPreco(produto_id=produto.id, preco=preco_novo))

    produto.preco_atual = preco_novo
    session.commit()

    if preco_anterior is None:
        logger.info(
            "Preço inicial registrado para '%s': R$ %s", produto.nome, preco_novo
        )
        return

    if preco_novo < preco_anterior:
        logger.info(
            "📉 Preço caiu! '%s': R$ %s -> R$ %s",
            produto.nome, preco_anterior, preco_novo
        )
        enviar_email_queda_preco(
            produto=produto,
            preco_anterior=preco_anterior,
            preco_novo=preco_novo
        )
    else:
        logger.info(
            "Sem queda para '%s' (preço atual: R$ %s)", produto.nome, preco_novo
        )