# Schemas para Emprestimo
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.book import LivroOut

class EmprestimoBase(BaseModel):
    usuario_id: int
    livro_id: int
    status: str

class EmprestimoCreate(EmprestimoBase):
    pass

class EmprestimoUpdate(BaseModel):
    status: Optional[str] = None

class EmprestimoOut(EmprestimoBase):
    id: int
    data_emprestimo: datetime
    data_devolucao: Optional[datetime]
    numero_renovacoes: int

    class Config:
        from_attributes = True

class EmprestimoLivroOut(EmprestimoOut):
    livro: LivroOut  # campo aninhado para o livro
    