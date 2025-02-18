from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Usuario as UsuarioModel
from app.schemas.user import UsuarioCreate, UsuarioOut, UsuarioUpdate, UsuarioCreateAdmin
from app.database import get_db
from app.services.security import get_current_user, bcrypt_context

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# Listar usuários (apenas "admin.read" pode listar todos os usuários)
@router.get("/", response_model=list[UsuarioOut])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if "admin.read" not in current_user.get("permissoes", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para visualizar usuários.")

    result = await db.execute(select(UsuarioModel))
    usuarios = result.scalars().all()
    return usuarios

# Obter usuário pelo ID (admin pode acessar qualquer um, clientes só acessam seus próprios dados)
@router.get("/{usuario_id}", response_model=UsuarioOut)
async def get_user(
    usuario_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    result = await db.execute(select(UsuarioModel).where(UsuarioModel.id == usuario_id))
    usuario = result.scalar_one_or_none()

    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    if usuario.id != current_user["id"] and "admin.read" not in current_user.get("permissoes", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para visualizar este usuário.")

    return usuario

# Criar usuário (apenas usuários com a permissão "admin.create" podem criar usuários)
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UsuarioOut)
async def create_user(
    create_user_request: UsuarioCreateAdmin,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if "admin.create" not in current_user.get("permissoes", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para criar usuários.")

    hashed_password = bcrypt_context.hash(create_user_request.senha_hash)

    novo_usuario = UsuarioModel(
        nome=create_user_request.nome,
        email=create_user_request.email,
        telefone=create_user_request.telefone,
        endereco_completo=create_user_request.endereco_completo,
        senha_hash=hashed_password,
        grupo_politica=create_user_request.grupo_politica # O admin tem permissão para conceder o grupo de política durante a criação
    )

    db.add(novo_usuario)
    try:
        await db.commit()
        await db.refresh(novo_usuario)
        return novo_usuario
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O email já está cadastrado.")

# Atualizar usuário (próprio usuário pode editar seus dados, admin pode editar qualquer um)
@router.put("/{usuario_id}", response_model=UsuarioOut)
async def update_user(
    usuario_id: int,
    update_data: UsuarioUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    result = await db.execute(select(UsuarioModel).where(UsuarioModel.id == usuario_id))
    usuario = result.scalar_one_or_none()

    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    # Administradores podem editar qualquer usuário
    if "admin.update" in current_user.get("permissoes", []):
        pass
    # Clientes podem editar apenas seus próprios dados
    elif "client.update_self" in current_user.get("permissoes", []):
        if usuario.id != current_user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para editar este usuário.")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para editar usuários.")

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(usuario, field, value)

    await db.commit()
    await db.refresh(usuario)
    return usuario

# Excluir usuário (apenas usuários com "admin.delete" podem excluir usuários)
@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    usuario_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if "admin.delete" not in current_user.get("permissoes", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para excluir usuários.")

    result = await db.execute(select(UsuarioModel).where(UsuarioModel.id == usuario_id))
    usuario = result.scalar_one_or_none()

    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    await db.delete(usuario)
    await db.commit()
    return
