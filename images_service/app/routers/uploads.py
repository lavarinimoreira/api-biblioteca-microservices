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

@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    x_api_key: str = Header(..., alias="X-API-KEY"),
    image_category: str = Header(...)
):
    # Verifica a API key
    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API Key inválida")
    
    # Cria o diretório para a categoria, se não existir
    category_path = os.path.join(UPLOAD_DIR, image_category)
    os.makedirs(category_path, exist_ok=True)
    
    # Gera um nome único para o arquivo mantendo a extensão original
    extension = os.path.splitext(file.filename)[1]
    unique_name = f"{uuid.uuid4().hex}{extension}"
    file_path = os.path.join(category_path, unique_name)
    
    # Salva o arquivo no sistema de arquivos
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {e}")
    
    # Monta a URL para acesso ao arquivo.
    # O hostname "images_service" será resolvido internamente via Docker
    file_url = f"http://images_service:8000/files/{image_category}/{unique_name}"
    
    return {"filename": unique_name, "file_url": file_url, "category": image_category}
