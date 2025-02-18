from typing import Optional
from pydantic import BaseModel

class GrupoPoliticaPermissaoBase(BaseModel):
    grupo_politica_nome: str
    permissao_namespace: str

class GrupoPoliticaPermissaoCreate(GrupoPoliticaPermissaoBase):
    pass

class GrupoPoliticaPermissaoUpdate(BaseModel):
    grupo_politica_nome: Optional[str]
    permissao_namespace: Optional[str]

class GrupoPoliticaPermissaoOut(GrupoPoliticaPermissaoBase):
    class Config:
        from_attributes = True