from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

"""
Observações:
Os três pontos (...) no Field(...) do Pydantic são uma forma de indicar que o campo é obrigatório.
-----------------------------------------------------------------------------------------------"""

# Schemas
class LivroCreate(BaseModel):
    titulo: str = Field(...)
    autor: str = Field(...)
    genero: Optional[str] = Field(None)
    editora: Optional[str] = Field(None)
    ano_publicacao: Optional[int] = Field(None, ge=0, le=2025)
    numero_paginas: Optional[int] = Field(None, ge=0, le=50560) # Tendo como base o livro "Das Buch des dickste Universum", o livro mais grosso do mundo, com 50.560 páginas.
    quantidade_disponivel: int = Field(..., ge=0, description="A quantidade deve ser zero ou positiva.")
    isbn: str = Field(...)
    image_url: Optional[str] = Field(None)  # Armazena a URL da capa
    """
    O Pydantic v2 mudou a forma de definir exemplos nos schemas.
    Antes, você podia passar example diretamente no Field, 
    mas agora isso deve ser feito usando o parâmetro json_schema_extra:
    """
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "titulo": "O Hobbit",
                    "autor": "J.R.R. Tolkien",
                    "genero": "Fantasia",
                    "editora": "HarperCollins",
                    "ano_publicacao": 1937,
                    "numero_paginas": 310,
                    "quantidade_disponivel": 5,
                    "isbn": "9780007525494"
                }
            ]
        }
    }

class LivroRead(BaseModel):
    id: int
    titulo: str
    autor: str
    genero: Optional[str]
    editora: Optional[str]
    ano_publicacao: Optional[int]
    numero_paginas: Optional[int]
    quantidade_disponivel: int
    isbn: str
    data_criacao: datetime
    data_atualizacao: datetime

    class Config:
        from_attributes = True


class LivroUpdate(BaseModel):
    titulo: Optional[str] = None
    autor: Optional[str] = None
    genero: Optional[str] = None
    editora: Optional[str] = None
    ano_publicacao: Optional[int] = None
    numero_paginas: Optional[int] = None
    quantidade_disponivel: Optional[int] = Field(None, ge=0, description="A quantidade deve ser zero ou positiva.")
    isbn: Optional[str] = None

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class LivroOut(BaseModel):
    id: int
    titulo: str
    autor: str
    genero: Optional[str]
    editora: Optional[str]
    ano_publicacao: Optional[int]
    numero_paginas: Optional[int]
    quantidade_disponivel: int
    isbn: str
    image_url: Optional[str] = Field(
        None, description="URL da capa do livro"
    )
    data_criacao: datetime
    data_atualizacao: datetime

    class Config:
        from_attributes = True
