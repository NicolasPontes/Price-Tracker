from abc import ABC, abstractmethod
from decimal import Decimal

class ProductScraper(ABC):
    @abstractmethod
    def get_product_data(self, url: str) -> dict:
        """
        Busca os dados de um produto através da URL.
        """

        pass