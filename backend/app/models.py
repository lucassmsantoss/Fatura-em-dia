"""Modelos SQLAlchemy — um usuário e toda a configuração/dados que pertencem a ele.

Pessoas, cartões e categorias são referenciados pelo NOME nos lançamentos
(como no protótipo original), não por chave estrangeira — isso mantém o
modelo simples e é suficiente para o escopo do projeto (1 usuário por conta,
sem pessoas com login próprio).
"""
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(200))
    onboarding_concluido: Mapped[bool] = mapped_column(default=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    pessoas: Mapped[list["Pessoa"]] = relationship(back_populates="usuario", cascade="all, delete-orphan")
    cartoes: Mapped[list["Cartao"]] = relationship(back_populates="usuario", cascade="all, delete-orphan")
    categorias: Mapped[list["Categoria"]] = relationship(back_populates="usuario", cascade="all, delete-orphan")
    regras: Mapped[list["Regra"]] = relationship(back_populates="usuario", cascade="all, delete-orphan")
    lancamentos: Mapped[list["Lancamento"]] = relationship(back_populates="usuario", cascade="all, delete-orphan")
    pagamentos: Mapped[list["Pagamento"]] = relationship(back_populates="usuario", cascade="all, delete-orphan")
    receitas: Mapped[list["Receita"]] = relationship(back_populates="usuario", cascade="all, delete-orphan")


class Pessoa(Base):
    __tablename__ = "pessoas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    nome: Mapped[str] = mapped_column(String(120))

    usuario: Mapped["Usuario"] = relationship(back_populates="pessoas")


class Cartao(Base):
    __tablename__ = "cartoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    nome: Mapped[str] = mapped_column(String(120))
    cor: Mapped[str] = mapped_column(String(20), default="#0E6F63")
    fecha: Mapped[int] = mapped_column(Integer, default=0)     # dia do fechamento (0 = não se aplica)
    desloca: Mapped[int] = mapped_column(Integer, default=0)    # meses até a fatura cobrar

    usuario: Mapped["Usuario"] = relationship(back_populates="cartoes")


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    nome: Mapped[str] = mapped_column(String(120))

    usuario: Mapped["Usuario"] = relationship(back_populates="categorias")


class Regra(Base):
    """Regra de auto-categorização: se a descrição contiver `chave`, sugere categoria/pessoas."""
    __tablename__ = "regras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    chave: Mapped[str] = mapped_column(String(120))
    categoria: Mapped[str] = mapped_column(String(120), default="")
    pessoas: Mapped[list[str]] = mapped_column(JSON, default=list)

    usuario: Mapped["Usuario"] = relationship(back_populates="regras")


class Lancamento(Base):
    __tablename__ = "lancamentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    data: Mapped[str] = mapped_column(String(10))          # AAAA-MM-DD (data da compra)
    mes: Mapped[str] = mapped_column(String(7), index=True)  # AAAA-MM (mês da fatura)
    descricao: Mapped[str] = mapped_column(String(200))
    categoria: Mapped[str] = mapped_column(String(120), default="")
    cartao: Mapped[str] = mapped_column(String(120), default="")
    parcela: Mapped[str] = mapped_column(String(20), default="")  # ex.: "2/4", vazio se à vista
    valor: Mapped[float] = mapped_column(Float)
    pessoas: Mapped[list[str]] = mapped_column(JSON, default=list)
    tipo: Mapped[str] = mapped_column(String(1), default="r")  # r=aconteceu · c=compromisso · e=estimativa

    usuario: Mapped["Usuario"] = relationship(back_populates="lancamentos")


class Pagamento(Base):
    """Registro de um pagamento recebido de uma pessoa, referente a um mês."""
    __tablename__ = "pagamentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    pessoa: Mapped[str] = mapped_column(String(120))
    valor: Mapped[float] = mapped_column(Float)
    data: Mapped[str] = mapped_column(String(10))
    mes_ref: Mapped[str] = mapped_column(String(7))
    obs: Mapped[str] = mapped_column(String(200), default="")

    usuario: Mapped["Usuario"] = relationship(back_populates="pagamentos")


class Receita(Base):
    """Receita mensal do usuário (para calcular sobra/falta no painel)."""
    __tablename__ = "receitas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    mes: Mapped[str] = mapped_column(String(7))
    renda_principal: Mapped[float] = mapped_column(Float, default=0)
    renda_extra: Mapped[float] = mapped_column(Float, default=0)

    usuario: Mapped["Usuario"] = relationship(back_populates="receitas")
