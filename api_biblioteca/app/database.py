from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()  # Carrega as variáveis do .env

DATABASE_URL = os.getenv("DATABASE_URL")

# Criação do async engine
engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True)

# Criação do async session factory
AsyncSessionLocal: AsyncSession = sessionmaker(autocommit=False, bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)

Base = declarative_base()

# Função para obter sessão do banco de dados
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session