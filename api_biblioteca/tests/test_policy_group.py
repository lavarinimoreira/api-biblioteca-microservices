import pytest
from httpx import AsyncClient
from fastapi import status

grupo_politica_data = {
    "nome": "moderador"
}

@pytest.mark.asyncio
async def test_criar_grupo_politica(client: AsyncClient, admin_auth_headers):
    # Criar Grupo de política
    response_grupo_politica = await client.post("/grupos_politica/", json=grupo_politica_data, headers=admin_auth_headers)
    assert response_grupo_politica.status_code == status.HTTP_201_CREATED
    grupo_politica_nome = response_grupo_politica.json()["nome"]
    assert grupo_politica_nome == "moderador"

@pytest.mark.asyncio
async def test_listar_grupos_politica(client: AsyncClient, admin_auth_headers):
    await client.post("/grupos_politica/", json={"nome": "super_usuario"}, headers=admin_auth_headers)
    await client.post("/grupos_politica/", json={"nome": "moderador"}, headers=admin_auth_headers)
    response = await client.get("/grupos_politica/", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

@pytest.mark.asyncio
async def test_obter_grupo_politica(client: AsyncClient, admin_auth_headers):
    # Cria um grupo para garantir que ele existe
    response = await client.post("/grupos_politica/", json={"nome": "Moderador"}, headers=admin_auth_headers)
    grupo_id = response.json()["id"]

    # Busca o grupo criado
    response = await client.get(f"/grupos_politica/{grupo_id}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == grupo_id
    assert data["nome"] == "Moderador"

@pytest.mark.asyncio
async def test_atualizar_grupo_politica(client: AsyncClient, admin_auth_headers):
    # Cria um grupo para atualizar
    response = await client.post("/grupos_politica/", json={"nome": "Usuario Comum"}, headers=admin_auth_headers)
    grupo_id = response.json()["id"]

    # Atualiza o nome do grupo
    response = await client.put(f"/grupos_politica/update/{grupo_id}", json={"nome": "Usuario Atualizado"}, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == grupo_id
    assert data["nome"] == "Usuario Atualizado"

@pytest.mark.asyncio
async def test_deletar_grupo_politica(client: AsyncClient, admin_auth_headers):
    # Cria um grupo para deletar
    response = await client.post("/grupos_politica/", json={"nome": "Grupo Temporario"}, headers=admin_auth_headers)
    grupo_id = response.json()["id"]

    # Deleta o grupo criado
    response = await client.delete(f"/grupos_politica/{grupo_id}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verifica se o grupo foi realmente deletado
    response = await client.get(f"/grupos_politica/{grupo_id}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
