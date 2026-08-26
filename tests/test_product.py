from decimal import Decimal

from app.services.product_service import cadastrar_produto


def testar_cadastro():

    produto = cadastrar_produto(
        nome="Teclado Mecânico",
        url="https://exemplo.com/teclado",
        preco_alvo=Decimal("250.00")
    )

    print("✅ Produto cadastrado!")
    print(f"ID: {produto.id}")
    print(f"Nome: {produto.nome}")
    print(f"Preço alvo: R$ {produto.preco_alvo}")


if __name__ == "__main__":
    testar_cadastro()