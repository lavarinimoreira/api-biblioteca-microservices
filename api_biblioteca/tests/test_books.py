import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.book import Livro as LivroModel
from fastapi import status

# Criar um livro com sucesso (ADMIN)
@pytest.mark.asyncio
async def test_criar_livro_sucesso(client: AsyncClient, async_session: AsyncSession, admin_auth_headers):
    novo_livro = {
        "titulo": "1984",
        "autor": "George Orwell",
        "genero": "Distopia",
        "editora": "Companhia das Letras",
        "ano_publicacao": 1949,
        "numero_paginas": 328,
        "quantidade_disponivel": 10,
        "isbn": "9788535902771"
    }

    response = await client.post("/livros/", json=novo_livro, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["titulo"] == "1984"

# Cliente NÃO pode criar um livro
@pytest.mark.asyncio
async def test_cliente_nao_pode_criar_livro(client: AsyncClient, client_auth_headers):
    novo_livro = {
        "titulo": "O Conto da Aia",
        "autor": "Margaret Atwood",
        "genero": "Distopia",
        "editora": "Rocco",
        "ano_publicacao": 1985,
        "numero_paginas": 336,
        "quantidade_disponivel": 5,
        "isbn": "9788532517653"
    }

    response = await client.post("/livros/", json=novo_livro, headers=client_auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN

# Listar livros e verificar se a busca funciona
@pytest.mark.asyncio
async def test_listar_livros_com_filtro(client: AsyncClient, admin_auth_headers):
    livros = [
        {
            "titulo": "O Senhor dos Anéis",
            "autor": "J.R.R. Tolkien",
            "genero": "Fantasia",
            "editora": "HarperCollins",
            "ano_publicacao": 1954,
            "numero_paginas": 1178,
            "quantidade_disponivel": 5,
            "isbn": "9780007525494"
        },
        {
            "titulo": "Duna",
            "autor": "Frank Herbert",
            "genero": "Ficção Científica",
            "editora": "Aleph",
            "ano_publicacao": 1965,
            "numero_paginas": 896,
            "quantidade_disponivel": 3,
            "isbn": "9788576572008"
        }
    ]

    for livro in livros:
        response = await client.post("/livros/", json=livro, headers=admin_auth_headers)
        assert response.status_code == status.HTTP_201_CREATED

    # Teste de busca por título
    response = await client.get("/livros/?titulo=Senhor")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["titulo"] == "O Senhor dos Anéis"

    # Teste de busca por autor
    response = await client.get("/livros/?autor=Tolkien")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["autor"] == "J.R.R. Tolkien"

    # Teste de busca por gênero
    response = await client.get("/livros/?genero=Fantasia")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["autor"] == "J.R.R. Tolkien"

# Obter livro inexistente (deve retornar 404)
@pytest.mark.asyncio
async def test_obter_livro_nao_existente(client: AsyncClient, admin_auth_headers):
    novo_livro = {
        "titulo": "1984",
        "autor": "George Orwell",
        "genero": "Distopia",
        "editora": "Companhia das Letras",
        "ano_publicacao": 1949,
        "numero_paginas": 328,
        "quantidade_disponivel": 10,
        "isbn": "9788535902771"
    }
    response = await client.post("/livros/", json=novo_livro, headers=admin_auth_headers)
    response = await client.get("/livros/9999")  # ID inexistente
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Livro não encontrado."

# Atualizar livro como ADMIN
@pytest.mark.asyncio
async def test_atualizar_livro(client: AsyncClient, async_session: AsyncSession, admin_auth_headers):
    livro = LivroModel(
        titulo="Harry Potter e a Pedra Filosofal",
        autor="J.K. Rowling",
        genero="Fantasia",
        editora="Rocco",
        ano_publicacao=1997,
        numero_paginas=223,
        quantidade_disponivel=8,
        isbn="9788532530785"
    )
    async_session.add(livro)
    await async_session.commit()

    update_data = {"quantidade_disponivel": 15}

    response = await client.put(f"/livros/{livro.id}", json=update_data, headers=admin_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["quantidade_disponivel"] == 15

# Cliente NÃO pode atualizar um livro
@pytest.mark.asyncio
async def test_cliente_nao_pode_atualizar_livro(client: AsyncClient, async_session: AsyncSession, client_auth_headers):
    livro = LivroModel(
        titulo="Fundação",
        autor="Isaac Asimov",
        genero="Ficção Científica",
        editora="Aleph",
        ano_publicacao=1951,
        numero_paginas=320,
        quantidade_disponivel=7,
        isbn="9788576572022"
    )
    async_session.add(livro)
    await async_session.commit()

    update_data = {"quantidade_disponivel": 20}

    response = await client.put(f"/livros/{livro.id}", json=update_data, headers=client_auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN

# Teste: Deletar um livro (ADMIN)
@pytest.mark.asyncio
async def test_deletar_livro(client: AsyncClient, async_session: AsyncSession, admin_auth_headers):
    livro = LivroModel(
        titulo="Neuromancer",
        autor="William Gibson",
        genero="Cyberpunk",
        editora="Aleph",
        ano_publicacao=1984,
        numero_paginas=271,
        quantidade_disponivel=3,
        isbn="9788576572008"
    )
    async_session.add(livro)
    await async_session.commit()

    # Deletar livro com autenticação
    response = await client.delete(f"/livros/{livro.id}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Buscar livro deletado com autenticação (forçar a passagem dos headers)
    response = await client.get(f"/livros/{livro.id}", headers=admin_auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND

