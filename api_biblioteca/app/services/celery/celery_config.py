# celery_config.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configuração do banco de dados síncrono para o Celery
DATABASE_URL_CELERY = "postgresql+psycopg2://dev_gabriel:university@biblioteca_db:5432/biblioteca_db"
engine = create_engine(DATABASE_URL_CELERY)
SessionLocalCelery = sessionmaker(autocommit=False, autoflush=False, bind=engine)