from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey
from sqlalchemy import Column, Integer, String
from .database import Base


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
    data = Column(Date, nullable=False)

    tipo = Column(String)  # fixo ou variavel
    categoria = Column(String)  # casa, meu, dela

    reembolsavel = Column(Boolean, default=False)
    quem_deve = Column(String, nullable=True)

    # para controle de parcelamento
    parcela_id = Column(Integer, nullable=True)
