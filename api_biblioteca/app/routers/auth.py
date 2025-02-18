from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from psycopg2 import IntegrityError
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt

from app.models.user import Usuario as UsuarioModel
from app.schemas.user import UsuarioCreate
from app.database import AsyncSessionLocal, get_db
from app.services.security import authenticate_user, create_access_token, bcrypt_context, oauth2_bearer

from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions import UniqueViolationError
from fastapi import HTTPException, status

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

class Token(BaseModel):
    access_token: str
    token_type: str

# Criar usuário
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: UsuarioCreate, db: AsyncSession = Depends(get_db)):
    novo_usuario = UsuarioModel(
        nome=create_user_request.nome,
        email=create_user_request.email,
        telefone=create_user_request.telefone,
        endereco_completo=create_user_request.endereco_completo,
        senha_hash=bcrypt_context.hash(create_user_request.senha_hash)
    )

    db.add(novo_usuario)
    try:
        await db.commit()
        await db.refresh(novo_usuario)
    except IntegrityError as e:
        await db.rollback()
        if isinstance(e.orig, UniqueViolationError):  # Verifica se o erro é de chave única
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{create_user_request.email}' já está cadastrado."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O email fornecido já está cadastrado."
        )

    return novo_usuario


# Login
@router.post("/token", status_code=status.HTTP_200_OK, response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
       raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Não foi possível validar o email.')
    
    # Correção: Passar o `db` corretamente para buscar permissões do usuário
    token = await create_access_token(user.email, user.id, user.grupo_politica, timedelta(minutes=20), db)

    return {'access_token': token, 'token_type': 'bearer'}

