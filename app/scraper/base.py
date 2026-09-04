from abc import ABC, abstractmethod
from decimal import Decimal

class ScraperBase(ABC):
    @abstractmethod
    def coletar_preco(self, url: str) -> Decimal:
        pass