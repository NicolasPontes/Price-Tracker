from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    produtos: Mapped[list["Produto"]] = relationship(
        back_populates="usuario", cascade="all, delete-orphan"
    )


class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    preco_atual: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=True)
    preco_alvo: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    usuario: Mapped["Usuario"] = relationship(back_populates="produtos")
    historico_precos: Mapped[list["HistoricoPreco"]] = relationship(
        back_populates="produto", cascade="all, delete-orphan"
    )


class HistoricoPreco(Base):
    __tablename__ = "historico_precos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    produto_id: Mapped[int] = mapped_column(ForeignKey("produtos.id"), nullable=False)

    preco: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    coletado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    produto: Mapped["Produto"] = relationship(back_populates="historico_precos")