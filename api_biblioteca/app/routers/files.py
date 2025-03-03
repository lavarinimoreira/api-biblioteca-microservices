from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
import os

from app.models.user import Usuario as UsuarioModel
from app.models.book import Livro as LivroModel
from app.schemas.book import LivroOut
from app.schemas.user import UsuarioOut
from app.database import get_db
from app.services.security import get_current_user

router = APIRouter(prefix="/images", tags=["Images"])

# Carrega a API key a partir da variável de ambiente
API_KEY = os.getenv("API_KEY", "CHAVE_SECRETA_PADRAO")

async def upload_imagem(file: UploadFile, image_category: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://images_service:8000/upload",  # Usando o nome do serviço definido no docker-compose
            files={"file": (file.filename, file.file, file.content_type)},
            headers={"X-API-KEY": API_KEY, "image-category": image_category}
        )
    return response

# # Adicionar imagem de perfil e atualizar o campo profile_picture_url do usuário
# @router.post("/profile", response_model=UsuarioOut, status_code=status.HTTP_200_OK)
# async def upload_profile_picture(
#     file: UploadFile = File(...),
#     current_user: dict = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     # Busca o usuário no banco de dados com base no ID contido no dicionário
#     stmt = select(UsuarioModel).where(UsuarioModel.id == current_user["id"])
#     result = await db.execute(stmt)
#     user = result.scalar_one_or_none()
#     if not user:
#         raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
#     response = await upload_imagem(file, "profile")
#     if response.status_code != 200:
#         raise HTTPException(status_code=500, detail="Erro ao enviar imagem para o serviço de imagens")
#     imagem_info = response.json()
    
#     # Atualiza a coluna profile_picture_url do usuário
#     user.profile_picture_url = imagem_info["file_url"]
#     await db.commit()
#     await db.refresh(user)
    
#     return user

@router.post("/profile/{user_id}", response_model=UsuarioOut, status_code=status.HTTP_200_OK)
async def upload_profile_picture_for_user(
    user_id: int,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Permite que um admin atualize qualquer perfil ou que o próprio usuário atualize o seu
    if current_user["id"] != user_id and "admin.update" not in current_user.get("permissoes", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para atualizar este usuário.")
    
    stmt = select(UsuarioModel).where(UsuarioModel.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
        
    response = await upload_imagem(file, "profile")
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro ao enviar imagem para o serviço de imagens")
    imagem_info = response.json()
    
    user.profile_picture_url = imagem_info["file_url"]
    await db.commit()
    await db.refresh(user)
    
    return user


# Adicionar imagem da capa do livro e atualizar o campo image_url do livro
@router.post("/book_cover", response_model=LivroOut, status_code=status.HTTP_200_OK)
async def upload_book_cover_image(
    # book_id: int,
    book_id: int = Form(...),  # utilizando Form(...) para receber o valor do formData
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verifica se o livro existe
    stmt = select(LivroModel).where(LivroModel.id == book_id)
    result = await db.execute(stmt)
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livro não encontrado")
    
    # Verifica se o usuário atual tem permissão para atualizar o livro
    if "book.create" not in current_user.get("permissoes", []):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissão negada.")
    
    response = await upload_imagem(file, "book_cover")
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro ao enviar imagem para o serviço de imagens")
    imagem_info = response.json()
    
    # Atualiza a coluna image_url do livro
    book.image_url = imagem_info["file_url"]
    await db.commit()
    await db.refresh(book)
    
    return book


