# celery_config.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração do banco de dados síncrono para o Celery
DATABASE_URL_CELERY = os.getenv("DATABASE_URL_CELERY")

# Verifica se a URL do banco de dados foi carregada corretamente
if not DATABASE_URL_CELERY:
    raise ValueError("A variável de ambiente DATABASE_URL_CELERY não foi configurada no arquivo .env")

# Cria a engine e a sessão do SQLAlchemy
engine = create_engine(DATABASE_URL_CELERY)
SessionLocalCelery = sessionmaker(autocommit=False, autoflush=False, bind=engine)