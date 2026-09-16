from urllib.parse import urlparse

from app.scraper.base import ProductScraper
from app.scraper.mercado_livre import MercadoLivreScraper

# Registro de domínio -> classe do scraper.
# Pra adicionar um novo site no futuro, basta implementar um novo
# ProductScraper e registrar aqui.
_SCRAPERS: dict[str, type[ProductScraper]] = {
    "mercadolivre.com.br": MercadoLivreScraper,
}


def get_scraper_for_url(url: str) -> ProductScraper:
    """
    Retorna uma instância do scraper adequado para a URL informada,
    com base no domínio.
    """

    hostname = urlparse(url).hostname or ""

    for domain, scraper_cls in _SCRAPERS.items():
        if hostname == domain or hostname.endswith(f".{domain}"):
            return scraper_cls()

    raise ValueError(
        f"Nenhum scraper disponível para o domínio '{hostname}'. "
        f"Domínios suportados: {', '.join(_SCRAPERS.keys())}"
    )