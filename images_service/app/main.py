# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import uploads

app = FastAPI()

app.include_router(uploads.router)

# Rota para servir os arquivos estáticos (imagens)
app.mount("/files", StaticFiles(directory="upload"), name="files")
