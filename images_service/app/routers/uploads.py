import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Header, status

router = APIRouter()

# Carrega a API key da variável de ambiente (ou usa um valor padrão)
API_KEY = os.getenv("API_KEY", "CHAVE_SECRETA_PADRAO")

# Diretório base para os uploads (mesmo nome usado no StaticFiles)
UPLOAD_DIR = "upload"

# Garante que o diretório base exista
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    x_api_key: str = Header(..., alias="X-API-KEY"),
    image_category: str = Header(...)
):
    # Verifica a API key
    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API Key inválida")
    
    # Verifica a extensão
    extension = os.path.splitext(file.filename)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de arquivo não permitido")
    
    # Lê os bytes para verificar o tamanho
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tamanho máximo de 5 MB excedido")
    
    # Gera um nome único para o arquivo mantendo a extensão original
    unique_name = f"{uuid.uuid4().hex}{extension}"
    category_path = os.path.join(UPLOAD_DIR, image_category)
    os.makedirs(category_path, exist_ok=True)
    file_path = os.path.join(category_path, unique_name)
    
    # Salva o arquivo no sistema de arquivos
    try:
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {e}")
    
    # Monta a URL para acesso ao arquivo.
    file_url = f"http://images_service:8000/files/{image_category}/{unique_name}"
    
    return {"filename": unique_name, "file_url": file_url, "category": image_category}

