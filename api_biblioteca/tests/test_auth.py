import pytest
from httpx import AsyncClient
from fastapi import status

# Dados para criação de usuário de teste
usuario = {
    "nome": "Gabriel Teste",
    "email": "gabriel_teste@example.com",
    "telefone": "123456789",
    "endereco_completo": "Rua de Teste, 123",
    "senha_hash": "senhaSegura123"
}

# Testes para a rota /auth/
@pytest.mark.asyncio
async def test_criar_usuario_sucesso(client: AsyncClient):
    """Teste para criar um usuário com sucesso."""
    response = await client.post("/auth/", json=usuario)
    assert response.status_code == status.HTTP_201_CREATED 
    assert response.json()["email"] == "gabriel_teste@example.com"


@pytest.mark.asyncio
async def test_criar_usuario_email_existente(client: AsyncClient):
    """Teste para tentar criar um usuário com um e-mail já cadastrado."""
    await client.post("/auth/", json=usuario)
    tentativa_de_cadastro_com_email_repetido = await client.post("/auth/", json=usuario)
    assert tentativa_de_cadastro_com_email_repetido.status_code == status.HTTP_400_BAD_REQUEST
    assert "já está cadastrado" in tentativa_de_cadastro_com_email_repetido.json()["detail"]


@pytest.mark.asyncio
async def test_criar_usuario_campos_incompletos(client: AsyncClient):
    """Teste para tentar criar um usuário sem preencher todos os campos obrigatórios."""
    payload = {
        "nome": "Usuário Incompleto",
        # Falta o campo 'email' e 'senha_hash'
        "telefone": "(31) 97777-7777",
        "endereco_completo": "Rua Faltando Campos, 999 - Bairro"
    }
    response = await client.post("/auth/", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY  # Erro de validação do Pydantic

# Testes para a rota de /auth/token
@pytest.mark.asyncio
async def test_login_sucesso(client: AsyncClient):
    """Teste para realizar login com sucesso."""
    payload = {
        "username": "cliente@biblioteca.com",  # Usuário válido
        "password": "cliente123"  # Senha correta
    }
    response = await client.post("/auth/token", data=payload)
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_credenciais_invalidas(client: AsyncClient):
    """Teste para tentar login com credenciais inválidas."""
    payload = {
        "username": "gabriel_teste@example.com",
        "password": "senhaerrada"  # Senha incorreta
    }
    response = await client.post("/auth/token", data=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Não foi possível validar o email."


@pytest.mark.asyncio
async def test_login_sem_credenciais(client: AsyncClient):
    """Teste para tentar login sem enviar credenciais."""
    payload = {}  # Nenhum dado enviado
    response = await client.post("/auth/token", data=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY