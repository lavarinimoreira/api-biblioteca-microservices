from datetime import timedelta, datetime, timezone  # Manipulação de datas e tempos para expiração de tokens
from sqlalchemy.future import select  # Consulta assíncrona com SQLAlchemy
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext  # Biblioteca para hashing de senhas
from jose import jwt, JWTError  # Biblioteca para geração e validação de tokens JWT
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer  # Esquema de autenticação para tokens OAuth2
from typing import Annotated  # Tipagem avançada para anotações de dependências

from app.models.user import Usuario as UsuarioModel
from app.models.policy_group import GrupoPolitica as GrupoPoliticaModel
from app.models.permission import Permissao as PermissaoModel

import os
from dotenv import load_dotenv  # Carregar variáveis de ambiente do arquivo .env

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações de segurança para JWT
SECRET_KEY = os.getenv("JWT_SECRET")  # Chave secreta usada para assinar tokens
ALGORITHM = os.getenv("ALGORITHM")  # Algoritmo utilizado para geração de tokens

# Configuração do bcrypt para hashing de senhas
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema de autenticação OAuth2, usado para obter tokens de acesso
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')


async def authenticate_user(email: str, password: str, db: AsyncSession):
    """Autentica um usuário verificando se o email existe e a senha está correta."""
    stmt = select(UsuarioModel).where(UsuarioModel.email == email)  # Consulta para buscar o usuário pelo email
    result = await db.execute(stmt)  # Executa a consulta
    user = result.scalar_one_or_none()  # Obtém o usuário encontrado ou None se não existir
    
    if not user:  # Se o usuário não for encontrado, retorna None
        return None
    
    # Verifica se a senha informada corresponde ao hash armazenado
    if not bcrypt_context.verify(password, user.senha_hash):
        return None 
    
    return user  # Retorna o usuário autenticado


async def create_access_token(username: str, user_id: int, grupo_politica: str, expires_delta: timedelta, db: AsyncSession):
    """Gera um token JWT contendo permissões associadas ao grupo de política do usuário."""

    # Buscar permissões associadas ao grupo de política do usuário
    result = await db.execute(
        select(PermissaoModel.namespace)
        .join(GrupoPoliticaModel.permissoes)  # Associa permissões pelo relacionamento muitos-para-muitos
        .where(GrupoPoliticaModel.nome == grupo_politica)
    )
    permissoes = [row[0] for row in result.fetchall()]  # Obtendo os namespaces das permissões

    # Definição do payload do token
    encode = {
        "sub": username,  # E-mail do usuário
        "id": user_id,  # ID do usuário
        "grupo_politica": grupo_politica,  # Nome do grupo de política
        "permissoes": permissoes  # Adicionando array de permissões ao token
    }

    # Calcula a data de expiração do token
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})  # Adiciona a expiração ao payload

    # Gera e retorna o token assinado
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    """Obtém o usuário autenticado a partir de um token JWT."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        grupo_politica: str = payload.get("grupo_politica")
        permissoes: list = payload.get("permissoes", [])

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Não foi possível validar o email."
            )

        return {
            "username": username,
            "id": user_id,
            "grupo_politica": grupo_politica,
            "permissoes": permissoes
        }
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido."
        )