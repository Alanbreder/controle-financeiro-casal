from pydantic import BaseModel
from typing import Optional


class LancamentoResponse(BaseModel):
    id: int
    descricao: str
    valor: float
    mes: int
    ano: int
    tipo: str
    categoria: str
    reembolsavel: bool
    quem_deve: Optional[str]
    parcelado: bool
    total_parcelas: Optional[int]
    numero_parcela: Optional[int]
    grupo_parcela: Optional[str]
    observacao: Optional[str]

    class Config:
        from_attributes = True
