from datetime import timedelta
from sqlalchemy import NullPool, insert, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
import pytest_asyncio
# import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.database import get_db
from app.models.__all_models import Base
from app.models.policy_group import GrupoPolitica as GrupoPoliticaModel
from app.models.permission import Permissao as PermissaoModel
from app.models.user import Usuario as UsuarioModel
from app.models.policy_group_permission import grupo_politica_permissao
from app.services.scripts.populate_permissions import permissoes  # Importa a lista de permissões
from app.services.scripts.populate_policy_group_permission import permissoes_admin, permissoes_cliente  # Importa a lista de relacionamento
from app.services.security import bcrypt_context, create_access_token

from dotenv import load_dotenv
import os

load_dotenv()  # Carrega as variáveis do .env


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

test_engine: AsyncEngine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True,
    poolclass=NullPool  # Desativa o pool de conexões, cada teste abre uma nova conexão isolada.
)

TestAsyncSessionLocal: AsyncSession = sessionmaker(
    autocommit=False,
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Configuração do banco de dados de teste
@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Limpeza do banco
        await conn.run_sync(Base.metadata.create_all)  # Criação das tabelas

    async with TestAsyncSessionLocal() as session:
        # Criando os grupos de política antes dos usuários
        grupo_politica_admin = GrupoPoliticaModel(nome="admin")
        grupo_politica_cliente = GrupoPoliticaModel(nome="cliente")
        session.add_all([grupo_politica_admin, grupo_politica_cliente])
        await session.commit()

        # Inserindo permissões no banco de testes
        for perm in permissoes:
            result = await session.execute(select(PermissaoModel).where(PermissaoModel.namespace == perm["namespace"]))
            if not result.scalar_one_or_none():
                session.add(PermissaoModel(**perm))
        await session.commit()

        # Recuperando os grupos de política do banco
        result_admin = await session.execute(select(GrupoPoliticaModel).where(GrupoPoliticaModel.nome == "admin"))
        grupo_admin = result_admin.scalar_one_or_none()

        result_cliente = await session.execute(select(GrupoPoliticaModel).where(GrupoPoliticaModel.nome == "cliente"))
        grupo_cliente = result_cliente.scalar_one_or_none()

        # Relacionando permissões ao grupo "admin"
        for namespace in permissoes_admin:
            result = await session.execute(select(PermissaoModel).where(PermissaoModel.namespace == namespace))
            permissao = result.scalar_one_or_none()
            if permissao:
                await session.execute(insert(grupo_politica_permissao).values(
                    grupo_politica_nome=grupo_admin.nome, permissao_namespace=permissao.namespace
                ))

        # Relacionando permissões ao grupo "cliente"
        for namespace in permissoes_cliente:
            result = await session.execute(select(PermissaoModel).where(PermissaoModel.namespace == namespace))
            permissao = result.scalar_one_or_none()
            if permissao:
                await session.execute(insert(grupo_politica_permissao).values(
                    grupo_politica_nome=grupo_cliente.nome, permissao_namespace=permissao.namespace
                ))

        # Criando um usuário administrador no banco de testes
        admin_email = "admin@biblioteca.com"
        admin_nome = "Administrador"
        admin_senha = "admin123"  # ALTERE APÓS TESTES SE NECESSÁRIO

        result_admin_user = await session.execute(select(UsuarioModel).where(UsuarioModel.email == admin_email))
        if not result_admin_user.scalar_one_or_none():
            novo_admin = UsuarioModel(
                nome=admin_nome,
                email=admin_email,
                telefone="(00) 00000-0000",
                endereco_completo="Endereço não especificado",
                senha_hash=bcrypt_context.hash(admin_senha),
                grupo_politica=grupo_admin.nome  # Definindo que o admin pertence ao grupo "admin"
            )
            session.add(novo_admin)
            print(f"Usuário admin criado: {admin_email} | Senha: {admin_senha}")

        # Criando um usuário cliente no banco de testes
        cliente_email = "cliente@biblioteca.com"
        cliente_nome = "Cliente Padrão"
        cliente_senha = "cliente123"

        result_cliente_user = await session.execute(select(UsuarioModel).where(UsuarioModel.email == cliente_email))
        if not result_cliente_user.scalar_one_or_none():
            novo_cliente = UsuarioModel(
                nome=cliente_nome,
                email=cliente_email,
                telefone="(11) 99999-9999",
                endereco_completo="Endereço de Teste",
                senha_hash=bcrypt_context.hash(cliente_senha),
                grupo_politica=grupo_cliente.nome  # Definindo que o cliente pertence ao grupo "cliente"
            )
            session.add(novo_cliente)

        await session.commit()

    yield  # Testes rodam após essa configuração

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Limpeza do banco após os testes


# Fixture que cria e gerencia a transação do banco para cada teste
@pytest_asyncio.fixture(scope="function")
async def async_session():
    async with test_engine.connect() as connection:
        # Inicia uma transação
        async with connection.begin() as transaction:
            session = TestAsyncSessionLocal(bind=connection)
            try:
                yield session  # Passa a sessão para o teste
            finally:
                await session.close()
                await transaction.rollback()  # Faz rollback para isolar o teste


# Fixture do cliente HTTP, sobrescrevendo a dependência do banco
@pytest_asyncio.fixture(scope="function")
async def client(async_session):
    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# Fixture para obter um token de ADMIN autenticado
@pytest_asyncio.fixture
async def token_admin(async_session):
    """Gera um token de acesso para o usuário admin"""
    result = await async_session.execute(select(UsuarioModel).where(UsuarioModel.email == "admin@biblioteca.com"))
    admin_user = result.scalar_one_or_none()

    # Gerando o token com as permissões associadas ao grupo
    token = await create_access_token(
        username=admin_user.email,
        user_id=admin_user.id,
        grupo_politica=admin_user.grupo_politica,  # Agora passamos o nome do grupo
        expires_delta=timedelta(minutes=60),
        db=async_session  # Passando a sessão do banco para buscar permissões
    )
    return token


# Fixture para obter um token de CLIENTE autenticado
@pytest_asyncio.fixture
async def token_cliente(async_session):
    """Gera um token de acesso para o usuário cliente"""
    result = await async_session.execute(select(UsuarioModel).where(UsuarioModel.email == "cliente@biblioteca.com"))
    cliente_user = result.scalar_one_or_none()

    # Gerando o token com as permissões associadas ao grupo
    token = await create_access_token(
        username=cliente_user.email,
        user_id=cliente_user.id,
        grupo_politica=cliente_user.grupo_politica,  # Nome do grupo de política
        expires_delta=timedelta(minutes=60),
        db=async_session  # Passando a sessão do banco para buscar permissões
    )
    return token

# Fixture para obter os headers de autenticação de um ADMIN
@pytest_asyncio.fixture
async def admin_auth_headers(token_admin):
    """Retorna os headers de autorização para um admin autenticado"""
    return {"Authorization": f"Bearer {token_admin}"}

# Fixture para obter os headers de autenticação de um CLIENTE
@pytest_asyncio.fixture
async def client_auth_headers(token_cliente):
    """Retorna os headers de autorização para um cliente autenticado"""
    return {"Authorization": f"Bearer {token_cliente}"}
