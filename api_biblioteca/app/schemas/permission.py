from pydantic import BaseModel
from datetime import datetime

class PermissaoBase(BaseModel):
    nome: str
    descricao: str | None = None
    namespace: str | None = None

class PermissaoCreate(PermissaoBase):
    pass

class PermissaoUpdate(PermissaoBase):
    pass

class PermissaoOut(PermissaoBase):
    id: int
    data_criacao: datetime
    data_atualizacao: datetime

    class Config:
        from_attributes = True