from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from app.models.policy_group import GrupoPolitica as GrupoPoliticaModel
from app.models.user import Usuario as UsuarioModel
from app.schemas.policy_group import GrupoPoliticaCreate, GrupoPoliticaOut, GrupoPoliticaUpdate
from app.database import get_db
from app.services.security import get_current_user


router = APIRouter(prefix="/grupos_politica", tags=["Grupos Politica"])

# Criar um novo grupo de políticas (apenas usuários com "policy_group.create" podem criar grupos de política)
@router.post("/", response_model=GrupoPoliticaOut, status_code=status.HTTP_201_CREATED)
async def criar_grupo_politica(grupo: GrupoPoliticaCreate, db: AsyncSession = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    # Validação de permissão
    if "policy_group.create" not in current_user.get("permissoes", []):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Acesso não autorizado. Falha de autenticação.')
    
    novo_grupo = GrupoPoliticaModel(nome=grupo.nome)
    db.add(novo_grupo)
    try:
        await db.commit()
        await db.refresh(novo_grupo)
        return novo_grupo
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nome do grupo já existe.")

# Listar grupos de política (permitido apenas a usuarios com a permissão "policy_group.read")
@router.get("/", response_model=list[GrupoPoliticaOut])
async def listar_grupos_politica(db: AsyncSession = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    # Validação de permissão
    if "policy_group.read" not in current_user.get("permissoes", []):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Acesso não autorizado. Falha de autenticação.')
    
    result = await db.execute(select(GrupoPoliticaModel))
    grupos = result.scalars().all()
    return grupos

# Exibir grupo de política por id (permitido apenas a usuarios com a permissão "policy_group.read")
@router.get("/{grupo_id}", response_model=GrupoPoliticaOut)
async def obter_grupo_politica(grupo_id: int, db: AsyncSession = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    # Validação de permissão
    if "policy_group.read" not in current_user.get("permissoes", []):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Acesso não autorizado. Falha de autenticação.')
    
    result = await db.execute(select(GrupoPoliticaModel).filter(GrupoPoliticaModel.id == grupo_id))
    grupo = result.scalars().first()
    if not grupo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado.")
    return grupo

# Atualizar grupo de política (permitido apenas a usuarios com a permissão "policy_group.update")
@router.put("/update/{grupo_id}", response_model=GrupoPoliticaOut)
async def atualizar_grupo_politica(grupo_id: int, grupo_update: GrupoPoliticaUpdate, db: AsyncSession = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    # Validação de permissão
    if "policy_group.update" not in current_user.get("permissoes", []):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Acesso não autorizado. Falha de autenticação.')
    
    result = await db.execute(select(GrupoPoliticaModel).filter(GrupoPoliticaModel.id == grupo_id))
    grupo = result.scalars().first()
    if not grupo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado.")

    grupo.nome = grupo_update.nome
    grupo.data_atualizacao = datetime.now()

    try:
        await db.commit()
        await db.refresh(grupo)
        return grupo
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nome do grupo já existe.")

# Deletar grupo de política (permitido apenas a usuarios com a permissão "policy_group.delete")
@router.delete("/{grupo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_grupo_politica(grupo_id: int, db: AsyncSession = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    # Validação de permissão
    if "policy_group.delete" not in current_user.get("permissoes", []):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Acesso não autorizado. Falha de autenticação.')
    
    result = await db.execute(select(GrupoPoliticaModel).filter(GrupoPoliticaModel.id == grupo_id))
    grupo = result.scalars().first()
    if not grupo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grupo não encontrado.")

    await db.delete(grupo)
    await db.commit()
    return None
