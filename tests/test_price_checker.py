from decimal import Decimal

from app.database.connection import SessionLocal
from app.database.models import Produto
from app.services.price_checker import verificar_precos
from app.services.product_service import cadastrar_produto

URL = "https://www.mercadolivre.com.br/canudo-sorvete-biju-sabor-baunilha-1kg-marvi/p/MLB22368489"


def garantir_produto_teste():
    """Cadastra o produto de teste só se ele ainda não existir (evita duplicar a cada execução)."""

    with SessionLocal() as session:
        existente = session.query(Produto).filter(Produto.url == URL).first()

        if existente:
            print(f"Produto de teste já existe (id={existente.id}).")
            return

    cadastrar_produto(
        nome="Canudo Sorvete Biju Baunilha 1kg",
        url=URL,
        preco_alvo=Decimal("25.00")
    )
    print("Produto de teste cadastrado.")


if __name__ == "__main__":
    garantir_produto_teste()

    print("\nRodando verificação de preços...\n")
    verificar_precos()

    print("\n✅ Verificação concluída. Confira a tabela historico_precos no banco.")