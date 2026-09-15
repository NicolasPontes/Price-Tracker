from app.scraper.mercado_livre import MercadoLivreScraper

URL = "https://www.mercadolivre.com.br/canudo-sorvete-biju-sabor-baunilha-1kg-marvi/p/MLB22368489?pdp_filters=item_id:MLB3680121572"

def testar_scraper():
    scraper = MercadoLivreScraper()
    produto = scraper.get_product_data(URL)

    print("\n✅ Produto encontrado!")
    print(f"Nome: {produto['nome']}")
    print(f"Preço: R$ {produto['preco']}")
    print(f"URL: {produto['url']}")

if __name__ == "__main__":
    testar_scraper()