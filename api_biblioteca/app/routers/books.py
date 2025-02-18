from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book import Livro as LivroModel
from app.schemas.book import LivroCreate, LivroRead, LivroUpdate
from app.database import get_db
from app.services.security import get_current_user

router = APIRouter(prefix="/livros", tags=["Livros"])


# Listar livros com filtros por título, autor e gênero
@router.get("/", response_model=List[LivroRead])
async def listar_livros(
    titulo: Optional[str] = Query(None, description="Filtrar por título do livro"),
    autor: Optional[str] = Query(None, description="Filtrar por autor"),
    genero: Optional[str] = Query(None, description="Filtrar por gênero"),
    skip: int = Query(0, ge=0, description="Número de registros para pular (paginação)"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de livros por página"),
    db: AsyncSession = Depends(get_db),
    # current_user: dict = Depends(get_current_user)
):
    query = select(LivroModel)

    if titulo:
        query = query.where(LivroModel.titulo.ilike(f"%{titulo}%"))  # Busca parcial (case insensitive)
    if autor:
        query = query.where(LivroModel.autor.ilike(f"%{autor}%"))
    if genero:
        query = query.where(LivroModel.genero.ilike(f"%{genero}%"))

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    livros = result.scalars().all()

    return livros

# Obter livro por ID
@router.get("/{livro_id}", response_model=LivroRead)
async def obter_livro(
    livro_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: dict = Depends(get_current_user)
):
    result = await db.execute(select(LivroModel).where(LivroModel.id == livro_id))
    livro = result.scalar_one_or_none()

    if not livro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado.")

    return livro


# Criar um novo livro (apenas administradores podem criar livros)
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=LivroRead)
async def criar_livro(
    livro_data: LivroCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if "book.create" not in current_user.get("permissoes", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para adicionar livros.")

    novo_livro = LivroModel(**livro_data.model_dump())

    db.add(novo_livro)
    try:
        await db.commit()
        await db.refresh(novo_livro)
        return novo_livro
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao adicionar o livro.")


# Atualizar livro (apenas administradores podem atualizar livros)
@router.put("/{livro_id}", response_model=LivroRead)
async def atualizar_livro(
    livro_id: int,
    livro_data: LivroUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if "book.update" not in current_user.get("permissoes", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para atualizar livros.")

    result = await db.execute(select(LivroModel).where(LivroModel.id == livro_id))
    livro = result.scalar_one_or_none()

    if not livro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado.")

    for field, value in livro_data.model_dump(exclude_unset=True).items():
        setattr(livro, field, value)

    await db.commit()
    await db.refresh(livro)
    return livro


# Excluir livro (apenas administradores podem excluir livros)
@router.delete("/{livro_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_livro(
    livro_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if "book.delete" not in current_user.get("permissoes", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para excluir livros.")

    result = await db.execute(select(LivroModel).where(LivroModel.id == livro_id))
    livro = result.scalar_one_or_none()

    if not livro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado.")

    await db.delete(livro)
    await db.commit()
