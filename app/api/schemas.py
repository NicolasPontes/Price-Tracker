from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field


# --- Produtos ---

class ProdutoCreate(BaseModel):
    url: str = Field(..., description="URL da página do produto em um site suportado")
    preco_alvo: Decimal = Field(..., gt=0, description="Você será avisado quando o preço cair a este valor ou menos")


class ProdutoUpdate(BaseModel):
    preco_alvo: Decimal | None = Field(None, gt=0)
    ativo: bool | None = None


class ProdutoOut(BaseModel):
    id: int
    nome: str
    url: str
    preco_atual: Decimal | None
    preco_alvo: Decimal
    ativo: bool
    criado_em: datetime

    class Config:
        from_attributes = True


class HistoricoPontoOut(BaseModel):
    preco: Decimal
    coletado_em: datetime

    class Config:
        from_attributes = True


# --- Autenticação / Usuários ---

class UsuarioCreate(BaseModel):
    email: EmailStr
    senha: str = Field(..., min_length=8, description="Mínimo de 8 caracteres")


class UsuarioOut(BaseModel):
    id: int
    email: str
    criado_em: datetime

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"