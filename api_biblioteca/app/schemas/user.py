from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime

# Base com campos comuns
class UsuarioBase(BaseModel):
    nome: str = Field(..., max_length=100)
    email: EmailStr
    telefone: Optional[str] = Field(None, max_length=15)
    endereco_completo: Optional[str] = Field(None, max_length=200)
    profile_picture_url: Optional[str] = Field(None)

# Schema para criação (inclui senha)
class UsuarioCreate(UsuarioBase):
    senha_hash: str = Field(..., min_length=8, max_length=128, description="A senha deve ter pelo menos 8 caracteres.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nome": "Mussum",
                    "email": "mussum@gmail.com",
                    "telefone": "(31)99999-9999",
                    "endereco_completo": "Rua Piracicaba, número 567, Bairro Floresta.",
                    "senha_hash": "SenhaSegura@123"
                }
            ]
        }
    }

# Schema específico para criação de Admins
class UsuarioCreateAdmin(UsuarioCreate):
    grupo_politica: Literal["admin", "cliente"] = Field(..., description="Grupo de política do usuário.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nome": "Novo Admin",
                    "email": "novo_admin@biblioteca.com",
                    "telefone": "(31)99999-9999",
                    "endereco_completo": "Rua Piracicaba, número 567, Bairro Floresta.",
                    "senha_hash": "SenhaAdmin123!",
                    "grupo_politica": "admin"
                }
            ]
        }
    }

# Schema para atualização de usuário
class UsuarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    telefone: Optional[str] = Field(None, max_length=15)
    endereco_completo: Optional[str] = Field(None, max_length=200)
    senha_hash: Optional[str] = Field(None, min_length=8, max_length=128)

class UsuarioAdminUpdate(UsuarioUpdate):
    grupo_politica: Optional[Literal["admin", "cliente"]] = None

# Schema para resposta (exclui a senha por segurança)
class UsuarioOut(UsuarioBase):
    id: int
    grupo_politica: str
    data_criacao: datetime
    data_atualizacao: Optional[datetime]
    
    class Config:
        from_attributes = True  # Permite conversão automática de ORM para Pydantic
