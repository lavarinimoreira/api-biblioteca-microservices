from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.models.permission import Permissao as PermissaoModel
from app.models.user import Usuario as UsuarioModel
from app.schemas.permission import PermissaoCreate, PermissaoOut, PermissaoUpdate
from app.database import get_db
from app.services.security import get_current_user
from datetime import datetime

router = APIRouter(prefix="/permissoes", tags=["Permissoes"])

# Criar uma nova permissão (apenas usuários com "admin.create" podem criar grupos de política)
@router.post("/", response_model=PermissaoOut, status_code=status.HTTP_201_CREATED)
async def criar_permissao(permissao: PermissaoCreate, db: AsyncSession = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    # Validação de permissão
    if "admin.create" not in current_user.get("permissoes", []):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Acesso não autorizado. Falha de autenticação.')
    
    nova_permissao = PermissaoModel(
        nome=permissao.nome,
        descricao=permissao.descricao,
        namespace=permissao.namespace
    )
    db.add(nova_permissao)
    try:
        await db.commit()
        await db.refresh(nova_permissao)
        return nova_permissao
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Permissão já existe.")

# Listar permissões (apenas usuários com "admin.read" podem criar grupos de política)
@router.get("/", response_model=list[PermissaoOut])
async def listar_permissoes(db: AsyncSession = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    # Validação de permissão
    if "admin.read" not in current_user.get("permissoes", []):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Acesso não autorizado. Falha de autenticação.')
    
    result = await db.execute(select(PermissaoModel))
    permissoes = result.scalars().all()
    return permissoes

# Listar permissão por id (apenas usuários com "admin.read" podem criar grupos de política)
@router.get("/{permissao_id}", response_model=PermissaoOut)
async def obter_permissao(permissao_id: int, db: AsyncSession = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    # Validação de permissão
    if "admin.read" not in current_user.get("permissoes", []):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Acesso não autorizado. Falha de autenticação.')
    
    result = await db.execute(select(PermissaoModel).filter(PermissaoModel.id == permissao_id))
    permissao = result.scalars().first()
    if not permissao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permissão não encontrada.")
    return permissao

# Atualizar uma permissão (apenas usuários com "admin.update" podem criar grupos de política)
@router.put("/{permissao_id}", response_model=PermissaoOut)
async def atualizar_permissao(permissao_id: int, permissao_update: PermissaoUpdate, db: AsyncSession = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    # Validação de permissão
    if "admin.update" not in current_user.get("permissoes", []):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Acesso não autorizado. Falha de autenticação.')
    
    result = await db.execute(select(PermissaoModel).filter(PermissaoModel.id == permissao_id))
    permissao = result.scalars().first()
    if not permissao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permissão não encontrada.")

    permissao.nome = permissao_update.nome
    permissao.descricao = permissao_update.descricao
    permissao.namespace = permissao_update.namespace
    permissao.data_atualizacao = datetime.now()

    try:
        await db.commit()
        await db.refresh(permissao)
        return permissao
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Permissão já existe.")

# Deletar permissão (apenas usuários com "admin.delete" podem criar grupos de política)
@router.delete("/{permissao_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_permissao(permissao_id: int, db: AsyncSession = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    # Validação de permissão
    if "admin.delete" not in current_user.get("permissoes", []):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Acesso não autorizado. Falha de autenticação.')
    
    result = await db.execute(select(PermissaoModel).filter(PermissaoModel.id == permissao_id))
    permissao = result.scalars().first()
    if not permissao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permissão não encontrada.")

    await db.delete(permissao)
    await db.commit()
    return None
