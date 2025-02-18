import pytest
from httpx import AsyncClient
from fastapi import status
from jose import jwt, JWTError

@pytest.mark.asyncio
async def test_create_user_admin(client: AsyncClient, admin_auth_headers):
    """Testa se um admin pode criar um usuário"""
    payload = {
        "nome": "Novo Usuário",
        "email": "novo_usuario@biblioteca.com",
        "telefone": "(31)99999-9999",
        "endereco_completo": "Rua Exemplo, 123",
        "senha_hash": "senhaForte123",
        "grupo_politica": "cliente"
    }

    response = await client.post("/usuarios/", json=payload, headers=admin_auth_headers)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["nome"] == payload["nome"]
    assert data["email"] == payload["email"]
    assert data["grupo_politica"] == "cliente"

@pytest.mark.asyncio
async def test_create_user_forbidden(client: AsyncClient, client_auth_headers):
    """Testa se um cliente comum NÃO pode criar um usuário"""
    payload = {
        "nome": "Usuário Teste",
        "email": "teste@biblioteca.com",
        "telefone": "(31)98888-7777",
        "endereco_completo": "Rua das Pedras, 45",
        "senha_hash": "senha12345",
        "grupo_politica": "cliente"
    }

    response = await client.post("/usuarios/", json=payload, headers=client_auth_headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Você não tem permissão para criar usuários."

import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_get_user_by_admin(client: AsyncClient, token_admin):
    """Testa se um ADMIN pode acessar qualquer usuário"""
    headers = {"Authorization": f"Bearer {token_admin}"}

    response = await client.get("/usuarios/2", headers=headers)  # Acessando cliente
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert data["id"] == 2  # Certifique-se de que esse ID existe no BD de testes
    assert "nome" in data
    assert "email" in data

@pytest.mark.asyncio
async def test_get_own_user_by_client(client: AsyncClient, token_cliente):
    """Testa se um CLIENTE pode acessar seus próprios dados"""
    headers = {"Authorization": f"Bearer {token_cliente}"}

    response = await client.get("/usuarios/2", headers=headers)  # O ID do cliente no BD de teste
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 2  # Cliente acessando ele mesmo

@pytest.mark.asyncio
async def test_client_cannot_access_other_user(client: AsyncClient, token_cliente):
    """Testa se um CLIENTE NÃO pode acessar outro usuário"""
    headers = {"Authorization": f"Bearer {token_cliente}"}

    response = await client.get("/usuarios/1", headers=headers)  # Tentando acessar admin (ID=1)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Você não tem permissão para visualizar este usuário."

@pytest.mark.asyncio
async def test_get_nonexistent_user(client: AsyncClient, token_admin):
    """Testa se um ADMIN recebe 404 ao buscar um usuário inexistente"""
    headers = {"Authorization": f"Bearer {token_admin}"}

    response = await client.get("/usuarios/999", headers=headers)  # ID inexistente
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Usuário não encontrado."

@pytest.mark.asyncio
async def test_list_users_by_admin(client: AsyncClient, token_admin):
    """Testa se um ADMIN pode listar todos os usuários"""
    headers = {"Authorization": f"Bearer {token_admin}"}

    response = await client.get("/usuarios/", headers=headers)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)  # Verifica se a resposta é uma lista
    assert len(data) > 0  # Deve conter pelo menos os usuários de teste

    # Verifica se cada usuário contém os campos esperados
    for user in data:
        assert "id" in user
        assert "nome" in user
        assert "email" in user
        assert "grupo_politica" in user

@pytest.mark.asyncio
async def test_client_cannot_list_users(client: AsyncClient, token_cliente):
    """Testa se um CLIENTE NÃO pode listar usuários"""
    headers = {"Authorization": f"Bearer {token_cliente}"}

    response = await client.get("/usuarios/", headers=headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Você não tem permissão para visualizar usuários."

@pytest.mark.asyncio
async def test_admin_can_update_any_user(client: AsyncClient, token_admin, async_session):
    """Testa se um ADMIN pode editar qualquer usuário"""
    headers = {"Authorization": f"Bearer {token_admin}"}

    # Pegando um usuário existente no banco de testes (exemplo: cliente)
    response = await client.get("/usuarios/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    usuarios = response.json()
    assert len(usuarios) > 0

    usuario_id = usuarios[0]["id"]  # Pegando um usuário qualquer

    payload = {"nome": "Nome Alterado pelo Admin"}
    response = await client.put(f"/usuarios/{usuario_id}", json=payload, headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["nome"] == payload["nome"]

@pytest.mark.asyncio
async def test_get_own_user_by_client(client: AsyncClient, token_cliente):
    """Testa se um CLIENTE pode atualizar seus próprios dados"""

    headers = {"Authorization": f"Bearer {token_cliente}"}
    payload = {
        "email": "novo_email@gmail.com"
    }

    # Decodificar o token JWT para obter o ID do usuário autenticado
    decoded_token = jwt.decode(token_cliente, key=None, options={"verify_signature": False})
    usuario_id = decoded_token.get("id")

    assert usuario_id, "ID do usuário não encontrado no token!"

    # Atualizar usuário autenticado
    response = await client.put(f"/usuarios/{usuario_id}", json=payload, headers=headers)

    assert response.status_code == status.HTTP_200_OK, f"Erro na atualização: {response.json()}"
    assert response.json()["email"] == payload["email"]

@pytest.mark.asyncio
async def test_client_cannot_update_other_user(client: AsyncClient, token_cliente):
    """Testa se um CLIENTE não pode atualizar os dados de outro usuário"""

    headers = {"Authorization": f"Bearer {token_cliente}"}
    payload = {
        "email": "email_nao_permitido@gmail.com"
    }

    # Decodificar o token JWT para obter o ID do usuário autenticado
    decoded_token = jwt.decode(token_cliente, key=None, options={"verify_signature": False})
    usuario_autenticado_id = decoded_token.get("id")

    assert usuario_autenticado_id, "ID do usuário autenticado não encontrado no token!"

    # Definir um ID de usuário diferente (exemplo: usuário autenticado = 2, tentar editar usuário ID = 1)
    usuario_alvo_id = 1 if usuario_autenticado_id != 1 else 2  # Garante que o alvo é diferente do autenticado

    # Tentar atualizar outro usuário
    response = await client.put(f"/usuarios/{usuario_alvo_id}", json=payload, headers=headers)

    # Garantir que a resposta seja 403 Forbidden
    assert response.status_code == status.HTTP_403_FORBIDDEN, f"Erro inesperado: {response.json()}"
    assert response.json()["detail"] == "Você não tem permissão para editar este usuário."

@pytest.mark.asyncio
async def test_updating_user_with_invalid_email(client: AsyncClient, token_cliente):
    """Testa se um CLIENTE não pode atualizar seus dados com um email inválido"""

    headers = {"Authorization": f"Bearer {token_cliente}"}
    payload = {"email": "email-invalido"}  # Email inválido

    decoded_token = jwt.decode(token_cliente, key=None, options={"verify_signature": False})
    usuario_id = decoded_token.get("id")

    response = await client.put(f"/usuarios/{usuario_id}", json=payload, headers=headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"Erro inesperado: {response.json()}"

@pytest.mark.asyncio
async def test_updating_non_existent_user_fails(client: AsyncClient, token_cliente):
    """Testa se tentar editar um usuário que não existe retorna 404"""

    headers = {"Authorization": f"Bearer {token_cliente}"}
    payload = {"email": "email@inexistente.com"}

    usuario_id_inexistente = 99999  # ID que não existe no banco de testes
    response = await client.put(f"/usuarios/{usuario_id_inexistente}", json=payload, headers=headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND, f"Erro inesperado: {response.json()}"
    assert response.json()["detail"] == "Usuário não encontrado."

@pytest.mark.asyncio
async def test_admin_can_delete_user(client: AsyncClient, token_admin):
    """Testa se um ADMIN pode excluir qualquer usuário"""
    
    headers = {"Authorization": f"Bearer {token_admin}"}

    # Criar um usuário de teste antes da exclusão (simulação)
    usuario_id_a_excluir = 2  # Supondo que este ID exista no banco de testes

    # Tentar excluir o usuário
    response = await client.delete(f"/usuarios/{usuario_id_a_excluir}", headers=headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT, f"Erro inesperado: {response.json()}"


@pytest.mark.asyncio
async def test_client_cannot_delete_user(client: AsyncClient, token_cliente):
    """Testa se um CLIENTE comum não pode excluir usuários"""

    headers = {"Authorization": f"Bearer {token_cliente}"}
    usuario_id_a_tentar_excluir = 2  # Um usuário qualquer no sistema

    response = await client.delete(f"/usuarios/{usuario_id_a_tentar_excluir}", headers=headers)

    assert response.status_code == status.HTTP_403_FORBIDDEN, f"Erro inesperado: {response.json()}"
    assert response.json()["detail"] == "Você não tem permissão para excluir usuários."


@pytest.mark.asyncio
async def test_delete_non_existent_user_fails(client: AsyncClient, token_admin):
    """Testa se tentar excluir um usuário inexistente retorna 404"""

    headers = {"Authorization": f"Bearer {token_admin}"}
    usuario_id_inexistente = 99999  # Um ID que certamente não existe no banco

    response = await client.delete(f"/usuarios/{usuario_id_inexistente}", headers=headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND, f"Erro inesperado: {response.json()}"
    assert response.json()["detail"] == "Usuário não encontrado."