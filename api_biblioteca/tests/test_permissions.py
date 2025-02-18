import pytest
from httpx import AsyncClient
from fastapi import status

permissao_data = {"nome": "Criar Usuarios", "descricao": "Permite criar usuários", "namespace": "criar.usuarios"}

@pytest.mark.asyncio
async def test_criar_permissao(client: AsyncClient, admin_auth_headers):
    response = await client.post("/permissoes/", json=permissao_data, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["nome"] == "Criar Usuarios"
    assert data["descricao"] == "Permite criar usuários"
    assert data["namespace"] == "criar.usuarios"
    assert "id" in data

@pytest.mark.asyncio
async def test_listar_permissoes(client: AsyncClient, admin_auth_headers):
    await client.post("/permissoes/", json=permissao_data, headers=admin_auth_headers)
    response = await client.get("/permissoes/", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

@pytest.mark.asyncio
async def test_obter_permissao(client: AsyncClient, admin_auth_headers):
    response = await client.post("/permissoes/", json=permissao_data, headers=admin_auth_headers)
    permissao_id = response.json()["id"]

    response = await client.get(f"/permissoes/{permissao_id}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == permissao_id
    assert data["nome"] == "Criar Usuarios"

@pytest.mark.asyncio
async def test_atualizar_permissao(client: AsyncClient, admin_auth_headers):
    response = await client.post("/permissoes/", json={"nome": "deletar_usuario", "descricao": "Permite deletar usuários", "namespace": "usuarios"}, headers=admin_auth_headers)
    permissao_id = response.json()["id"]

    response = await client.put(f"/permissoes/{permissao_id}", json={"nome": "remover_usuario", "descricao": "Permite remover usuários", "namespace": "usuarios"}, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == permissao_id
    assert data["nome"] == "remover_usuario"

@pytest.mark.asyncio
async def test_deletar_permissao(client: AsyncClient, admin_auth_headers):
    response = await client.post("/permissoes/", json={"nome": "visualizar_logs", "descricao": "Permite visualizar logs", "namespace": "logs"}, headers=admin_auth_headers)
    permissao_id = response.json()["id"]

    response = await client.delete(f"/permissoes/{permissao_id}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = await client.get(f"/permissoes/{permissao_id}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
