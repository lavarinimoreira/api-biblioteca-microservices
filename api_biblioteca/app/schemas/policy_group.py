from pydantic import BaseModel
from datetime import datetime

class GrupoPoliticaBase(BaseModel):
    nome: str

class GrupoPoliticaCreate(GrupoPoliticaBase):
    pass

class GrupoPoliticaUpdate(GrupoPoliticaBase):
    pass

class GrupoPoliticaOut(GrupoPoliticaBase):
    id: int
    data_criacao: datetime
    data_atualizacao: datetime

    class Config:
        from_attributes = True