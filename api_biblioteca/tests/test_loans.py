import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.security import SECRET_KEY, ALGORITHM

# Dados para criação do livro de teste
livro_data = {
    "titulo": "O Hobbit",
    "autor": "J.R.R. Tolkien",
    "genero": "Fantasia",
    "editora": "HarperCollins",
    "ano_publicacao": 1937,
    "numero_paginas": 310,
    "quantidade_disponivel": 5,
    "isbn": "9780007525492"
}

# Deve ser permitido a criação de um empréstimo por um admim
@pytest.mark.asyncio
async def test_criar_emprestimo(client: AsyncClient, admin_auth_headers):
    # Criar livro
    response_livro = await client.post("/livros/", json=livro_data, headers=admin_auth_headers)
    assert response_livro.status_code == status.HTTP_201_CREATED
    livro_id = response_livro.json()["id"]

    # Criar empréstimo
    emprestimo_data = {
        "usuario_id": 2, 
        "livro_id": livro_id,  
        "status": "Ativo"
    }
    response_emprestimo = await client.post("/emprestimos/", json=emprestimo_data, headers=admin_auth_headers)  # Adicionando autenticação
    assert response_emprestimo.status_code == status.HTTP_201_CREATED
    emprestimo = response_emprestimo.json()
    assert emprestimo["usuario_id"] == 2
    assert emprestimo["livro_id"] == livro_id
    assert emprestimo["status"] == "Ativo"

# Deve ser nagada a criação de um empréstimo por um cliente
@pytest.mark.asyncio
async def test_cliente_criar_emprestimo(client: AsyncClient, client_auth_headers, admin_auth_headers):
    # Criar livro
    response_livro = await client.post("/livros/", json=livro_data, headers=admin_auth_headers)
    assert response_livro.status_code == status.HTTP_201_CREATED
    livro_id = response_livro.json()["id"]

    # Criar empréstimo
    emprestimo_data = {
        "usuario_id": 2, 
        "livro_id": livro_id,  
        "status": "Ativo"
    }
    response_emprestimo = await client.post("/emprestimos/", json=emprestimo_data, headers=client_auth_headers)  # Adicionando autenticação
    assert response_emprestimo.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_listar_meus_emprestimos(client: AsyncClient, async_session: AsyncSession, admin_auth_headers, client_auth_headers):
    # Criar livro
    response_livro = await client.post("/livros/", json=livro_data, headers=admin_auth_headers)
    assert response_livro.status_code == status.HTTP_201_CREATED
    livro_id = response_livro.json()["id"]

    # Criar empréstimo
    emprestimo_data = {
        "usuario_id": 2, 
        "livro_id": livro_id,  
        "status": "Ativo"
    }
    response_emprestimo = await client.post("/emprestimos/", json=emprestimo_data, headers=admin_auth_headers)  # Adicionando autenticação
    assert response_emprestimo.status_code == status.HTTP_201_CREATED

    # Buscar os empréstimos do usuário autenticado
    response = await client.get("/emprestimos/", headers=client_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0  # Verificar se a lista não está vazia

# Teste para leitura de um empréstimo a partir de seu id
@pytest.mark.asyncio
async def test_obter_emprestimo_por_id(client: AsyncClient, admin_auth_headers):
     # Criar livro
    response_livro = await client.post("/livros/", json=livro_data, headers=admin_auth_headers)
    livro_id = response_livro.json()["id"]

    # Criar empréstimo
    emprestimo_data = {
        "usuario_id": 2, 
        "livro_id": livro_id,  
        "status": "Ativo"
    }
    response_emprestimo = await client.post("/emprestimos/", json=emprestimo_data, headers=admin_auth_headers)
    emprestimo_id = response_emprestimo.json()["id"]  # Obtendo o ID do empréstimo criado

    # Buscar o empréstimo pelo ID
    response_emprestimo_get = await client.get(f"/emprestimos/{emprestimo_id}", headers=admin_auth_headers)
    print(response_emprestimo_get.status_code)  # Depuração: Verificar o status code
    print(response_emprestimo_get.json())  # Depuração: Verificar a resposta

    # Verificar se o ID do empréstimo retornado é o mesmo que foi criado
    emprestimo_get_by_id = response_emprestimo_get.json()["id"]
    assert emprestimo_id == emprestimo_get_by_id


# Teste para renovação de empréstimo
@pytest.mark.asyncio
async def test_renovar_emprestimo(client: AsyncClient, admin_auth_headers):
    # Criar livro
    response_livro = await client.post("/livros/", json=livro_data, headers=admin_auth_headers)
    livro_id = response_livro.json()["id"]

    # Criar emprestimo
    emprestimo_data = {
        "usuario_id": 2,
        "livro_id": livro_id,
        "status": "Ativo"
    }
    response_emprestimo = await client.post("/emprestimos/", json=emprestimo_data, headers=admin_auth_headers)
    emprestimo_id = response_emprestimo.json()["id"]  # Obtendo o ID do empréstimo criado

     # Realizar até 3 renovações permitidas
    for i in range(1, 4):  # 1ª, 2ª e 3ª renovação
        response_renovacao = await client.put(f"/emprestimos/{emprestimo_id}", json={"status": "Renovado"}, headers=admin_auth_headers)
        assert response_renovacao.status_code == status.HTTP_200_OK
        emprestimo_renovado = response_renovacao.json()
        assert emprestimo_renovado["numero_renovacoes"] == i

    # Tentar a 4ª renovação, que deve ser negada
    response_renovacao_negada = await client.put(f"/emprestimos/{emprestimo_id}", json={"status": "Renovado"}, headers=admin_auth_headers)
    assert response_renovacao_negada.status_code == status.HTTP_400_BAD_REQUEST

# Teste para devolução de livro
@pytest.mark.asyncio
async def test_devolver_emprestimo(client: AsyncClient, admin_auth_headers):
    # Criar livro
    response_livro = await client.post("/livros/", json=livro_data, headers=admin_auth_headers)
    livro_id = response_livro.json()["id"]

    # Criar emprestimo
    emprestimo_data = {
        "usuario_id": 2,
        "livro_id": livro_id,
        "status": "Ativo"
    }
    response_emprestimo = await client.post("/emprestimos/", json=emprestimo_data, headers=admin_auth_headers)
    emprestimo_id = response_emprestimo.json()["id"]  # Obtendo o ID do empréstimo criado

    # Atualizando o status para devolução
    response_devolucao = await client.put(f"/emprestimos/{emprestimo_id}", json={"status": "Devolvido"}, headers=admin_auth_headers)
    assert response_devolucao.status_code == status.HTTP_200_OK
    emprestimo_devolvido = response_devolucao.json()
    assert emprestimo_devolvido["status"] == "Devolvido"

# Teste para deletar empréstimo
@pytest.mark.asyncio
async def test_deletar_emprestimo(client: AsyncClient, admin_auth_headers):
     # Criar livro
    response_livro = await client.post("/livros/", json=livro_data, headers=admin_auth_headers)
    livro_id = response_livro.json()["id"]

    # Criar emprestimo
    emprestimo_data = {
        "usuario_id": 2,
        "livro_id": livro_id,
        "status": "Ativo"
    }
    response_emprestimo = await client.post("/emprestimos/", json=emprestimo_data, headers=admin_auth_headers)
    emprestimo_id = response_emprestimo.json()["id"]  # Obtendo o ID do empréstimo criado

    # Deletar emprestimo
    response_delete = await client.delete(f"/emprestimos/{emprestimo_id}", headers=admin_auth_headers)
    assert response_delete.status_code == status.HTTP_204_NO_CONTENT

    # Verificar que o emprestimo foi deletado
    response_verificar = await client.get(f"/emprestimos/{emprestimo_id}", headers=admin_auth_headers)
    assert response_verificar.status_code == status.HTTP_404_NOT_FOUND