from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, delete
from app.models.policy_group_permission import grupo_politica_permissao
from app.models.user import Usuario as UsuarioModel
from app.schemas.policy_group_permission import GrupoPoliticaPermissaoCreate, GrupoPoliticaPermissaoOut
from app.database import get_db
from app.services.security import get_current_user

router = APIRouter(prefix="/grupo_politica_permissoes", tags=["Grupo Politica Permissoes"])


# Criar uma novo relacionamento entre Grupo de política e Permissão (apenas usuários com "admin.create" podem criar grupos de política)
@router.post("/", response_model=GrupoPoliticaPermissaoOut, status_code=status.HTTP_201_CREATED)
async def adicionar_permissao_ao_grupo(relacao: GrupoPoliticaPermissaoCreate, db: AsyncSession = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    # Validação de permissão
    if "admin.create" not in current_user.get("permissoes", []):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Acesso não autorizado. Falha de autenticação.')
    
    stmt = insert(grupo_politica_permissao).values(
        grupo_politica_nome=relacao.grupo_politica_nome,
        permissao_namespace=relacao.permissao_namespace
    )
    try:
        await db.execute(stmt)
        await db.commit()
        return relacao
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao adicionar permissão ao grupo.")

# Criar uma novo relacionamento entre Grupo de política e Permissão (apenas usuários com "admin.read" podem criar grupos de política)
@router.get("/", response_model=list[GrupoPoliticaPermissaoOut])
async def listar_permissoes_grupo(db: AsyncSession = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    # Validação de permissão
    if "admin.read" not in current_user.get("permissoes", []):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Acesso não autorizado. Falha de autenticação.')
    
    result = await db.execute(select(grupo_politica_permissao))
    permissoes_grupos = result.fetchall()
    return [{"grupo_politica_nome": row.grupo_politica_nome, "permissao_namespace": row.permissao_namespace} for row in permissoes_grupos]

# Excluir relacionamento entre Grupo de política e Permissão (permitido apenas a usuários com namespace "admin.delete")
@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def remover_permissao_do_grupo(grupo_politica_nome: str, permissao_namespace: str, db: AsyncSession = Depends(get_db), current_user: UsuarioModel = Depends(get_current_user)):
    # Validação de permissão
    if "admin.delete" not in current_user.get("permissoes", []):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Acesso não autorizado. Falha de autenticação.')
    
    stmt = delete(grupo_politica_permissao).where(
        grupo_politica_permissao.c.grupo_politica_nome == grupo_politica_nome,
        grupo_politica_permissao.c.permissao_namespace == permissao_namespace
    )
    result = await db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relacionamento não encontrado.")

    await db.commit()
    return None