import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_adicionar_permissao_ao_grupo(client: AsyncClient, admin_auth_headers):
    # Criar um grupo e uma permissao para associar
    grupo_response = await client.post("/grupos_politica/", json={"nome": "Admin"}, headers=admin_auth_headers)
    permissao_response = await client.post("/permissoes/", json={"nome": "criar_usuario", "descricao": "Permite criar usuários", "namespace": "usuarios"}, headers=admin_auth_headers)

    grupo_politica_nome = grupo_response.json()["nome"]
    permissao_namespace = permissao_response.json()["namespace"]

    # Associar permissao ao grupo
    response = await client.post("/grupo_politica_permissoes/", json={"grupo_politica_nome": grupo_politica_nome, "permissao_namespace": permissao_namespace}, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["grupo_politica_nome"] == grupo_politica_nome
    assert data["permissao_namespace"] == permissao_namespace

@pytest.mark.asyncio
async def test_listar_permissoes_grupo(client: AsyncClient, admin_auth_headers):
    # Criar um grupo e uma permissão para garantir que há dados
    grupo_response = await client.post("/grupos_politica/", json={"nome": "Teste Grupo"}, headers=admin_auth_headers)
    permissao_response = await client.post("/permissoes/", json={
        "nome": "acessar_dashboard", 
        "descricao": "Permite acessar o dashboard", 
        "namespace": "dashboard"
    }, headers=admin_auth_headers)

    grupo_politica_nome = grupo_response.json()["id"]
    permissao_namespace = permissao_response.json()["id"]

    # Associar permissão ao grupo
    await client.post("/grupo_politica_permissoes/", json={
        "grupo_politica_nome": grupo_politica_nome,
        "permissao_namespace": permissao_namespace
    }, headers=admin_auth_headers)

    # Listar as permissões do grupo
    response = await client.get("/grupo_politica_permissoes/", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0  # Agora deve ter pelo menos uma associação


@pytest.mark.asyncio
async def test_remover_permissao_do_grupo(client: AsyncClient, admin_auth_headers):
    # Criar um grupo e uma permissao para associar e depois remover
    grupo_response = await client.post("/grupos_politica/", json={"nome": "Moderador"}, headers=admin_auth_headers)
    permissao_response = await client.post("/permissoes/", json={"nome": "editar_conteudo", "descricao": "Permite editar conteúdos", "namespace": "conteudo"}, headers=admin_auth_headers)

    grupo_politica_nome = grupo_response.json()["nome"]
    permissao_namespace = permissao_response.json()["namespace"]

    # Associar permissao ao grupo
    await client.post("/grupo_politica_permissoes/", json={"grupo_politica_nome": grupo_politica_nome, "permissao_namespace": permissao_namespace}, headers=admin_auth_headers)

    # Remover a permissao do grupo
    response = await client.delete(f"/grupo_politica_permissoes/?grupo_politica_nome={grupo_politica_nome}&permissao_namespace={permissao_namespace}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Confirmar que a permissao foi removida
    response = await client.get("/grupo_politica_permissoes/", headers=admin_auth_headers)
    data = response.json()
    assert {"grupo_politica_nome": grupo_politica_nome, "permissao_namespace": permissao_namespace} not in data