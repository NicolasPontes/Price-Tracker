from decimal import Decimal

from app.database.connection import SessionLocal
from app.database.models import Produto
from app.services.price_checker import verificar_precos

URL = "https://www.mercadolivre.com.br/canudo-sorvete-biju-sabor-baunilha-1kg-marvi/p/MLB22368489"


def forcar_preco_alto_artificialmente():
    """
    Define um preço artificialmente ALTO como 'preço atual' salvo no banco,
    pra garantir que o próximo preço real coletado da API seja menor —
    forçando a detecção de queda e o disparo do e-mail.
    """

    with SessionLocal() as session:
        produto = session.query(Produto).filter(Produto.url == URL).first()

        if not produto:
            print("❌ Produto de teste não encontrado. Rode tests/test_price_checker.py primeiro.")
            return

        preco_antigo = produto.preco_atual
        produto.preco_atual = Decimal("9999.99")
        session.commit()

        print(f"Preço artificial definido: {preco_antigo} -> 9999.99")


if __name__ == "__main__":
    forcar_preco_alto_artificialmente()

    print("\nRodando verificação (deve detectar queda e enviar e-mail)...\n")
    verificar_precos()

    print("\n✅ Verificação concluída. Confira sua caixa de entrada!")