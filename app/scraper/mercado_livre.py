import re

import requests

from app.auth.mercado_livre_auth import get_valid_access_token
from app.scraper.base import ProductScraper


class MercadoLivreScraper(ProductScraper):
    """
    Scraper do Mercado Livre baseado na API oficial, autenticado via OAuth2.

    Histórico de decisões (documentado pra não repetir os mesmos erros):
    - HTML parsing (BeautifulSoup) direto no site: descartado, o ML bloqueia
      requests simples e o HTML retornado nem sempre é a página real.
    - `/items/{item_id}` com o item_id específico da oferta (ex: vindo de
      `item_id:MLB...` na URL): descartado, retorna 403 access_denied.
      Esse tipo de item_id (originado de intervenção de carrinho/recomendação)
      não é liberado para consulta direta via API por apps de terceiros.
    - Solução atual: usar o `catalog_product_id` (o ID que aparece em
      `/p/MLB...` na URL) com dois endpoints públicos:
        1. GET /products/{id}       -> nome do produto
        2. GET /products/{id}/items -> lista de ofertas com preço
      O primeiro item da lista é a oferta "vencedora" (buy box) daquele
      produto — é o preço que aparece em destaque na página.
    """

    PRODUCT_URL = "https://api.mercadolibre.com/products/{product_id}"
    PRODUCT_ITEMS_URL = "https://api.mercadolibre.com/products/{product_id}/items"

    def get_product_data(self, url: str) -> dict:

        product_id = self._extrair_catalog_product_id(url)

        access_token = get_valid_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}

        nome = self._buscar_nome(product_id, headers)
        preco, item_url = self._buscar_menor_preco(product_id, headers)

        return {
            "nome": nome,
            "preco": preco,
            "url": item_url or url
        }

    def _buscar_nome(self, product_id: str, headers: dict) -> str:

        response = requests.get(
            self.PRODUCT_URL.format(product_id=product_id),
            headers=headers,
            timeout=15
        )
        response.raise_for_status()

        data = response.json()

        if "name" not in data:
            raise ValueError(
                f"Resposta da API não contém o nome do produto {product_id}."
            )

        return data["name"]

    def _buscar_menor_preco(self, product_id: str, headers: dict) -> tuple[float, str | None]:

        response = requests.get(
            self.PRODUCT_ITEMS_URL.format(product_id=product_id),
            headers=headers,
            timeout=15
        )
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        if not results:
            raise ValueError(
                f"Nenhuma oferta encontrada para o produto {product_id}."
            )

        # O primeiro resultado é a oferta em destaque (buy box) do produto.
        oferta_principal = results[0]

        item_url = f"https://www.mercadolivre.com.br/p/{product_id}"

        return oferta_principal["price"], item_url

    def _extrair_catalog_product_id(self, url: str) -> str:
        """
        Extrai o ID do produto de catálogo (ex: MLB22368489) da URL,
        a partir do padrão /p/MLB.... Esse é o ID "pai" do produto,
        não o item_id de uma oferta específica.
        """

        match = re.search(r"/p/(MLB\d+)", url)
        if match:
            return match.group(1)

        # fallback: primeiro MLB\d+ encontrado na URL
        match = re.search(r"(MLB\d+)", url)
        if match:
            return match.group(1)

        raise ValueError(
            f"Não foi possível extrair o ID do produto de catálogo da URL: {url}"
        )