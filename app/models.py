from sqlalchemy import Column, Integer, String, Float, Boolean
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)


class Lancamento(Base):
    __tablename__ = "lancamentos"

    id = Column(Integer, primary_key=True, index=True)

    descricao = Column(String, nullable=False)
    valor = Column(Float, nullable=False)

    mes = Column(Integer, nullable=False)
    ano = Column(Integer, nullable=False)

    tipo = Column(String, nullable=False)
    categoria = Column(String, nullable=False)

    reembolsavel = Column(Boolean, default=False)
    quem_deve = Column(String, nullable=True)

    parcelado = Column(Boolean, default=False)
    total_parcelas = Column(Integer, nullable=True)
    numero_parcela = Column(Integer, nullable=True)
    grupo_parcela = Column(String, nullable=True)

    observacao = Column(String, nullable=True)
