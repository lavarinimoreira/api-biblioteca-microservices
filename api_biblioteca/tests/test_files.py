import pytest
from httpx import AsyncClient

from app.models.book import Livro as LivroModel

# O monkeypatch sobrescreverá a função upload_imagem usada nessa rota.
@pytest.mark.asyncio
async def test_upload_profile_picture(client, admin_auth_headers, monkeypatch):
    # Função fake que simula o upload da imagem e retorna uma resposta dummy
    async def fake_upload_imagem(file, category: str):
        class DummyResponse:
            status_code = 200

            def json(self):
                return {"file_url": "http://images_service:8000/files/profile/dummy.png"}
        return DummyResponse()

    # Sobrescreve a função upload_imagem na rota onde ela é importada/utilizada.
    monkeypatch.setattr("app.routers.files.upload_imagem", fake_upload_imagem)

    # Simula o envio de um arquivo de imagem (conteúdo fictício)
    file_content = b"conteudo_imagem_dummy"
    files = {"file": ("dummy.png", file_content, "image/png")}

    # Realiza a requisição para a rota /profile, passando os headers de autenticação
    response = await client.post("/images/profile", files=files, headers=admin_auth_headers)
    
    # Verifica se a resposta foi bem-sucedida (HTTP 200)
    assert response.status_code == 200
    data = response.json()

    # Confirma que a URL da imagem foi atualizada conforme o retorno do fake_upload_imagem
    assert data.get("profile_picture_url") == "http://images_service:8000/files/profile/dummy.png"


# Teste adicionar capa de livro
@pytest.mark.asyncio
async def test_upload_book_cover_image(client, admin_auth_headers, monkeypatch, async_session):
    # Cria um livro dummy na base de testes
    dummy_book = LivroModel(
        id=1,
        titulo="1984",
        autor="George Orwell",
        genero="Distopia",
        editora="Companhia das Letras",
        ano_publicacao=1949,
        numero_paginas=328,
        quantidade_disponivel=10,
        isbn="9788535902771",
        image_url=None
    )
    async_session.add(dummy_book)
    await async_session.commit()

    # Sobrescreve a função upload_imagem para simular um upload bem-sucedido
    async def fake_upload_imagem(file, category: str):
        class DummyResponse:
            status_code = 200

            def json(self):
                return {"file_url": f"http://images_service:8000/files/{category}/dummy.png"}
        return DummyResponse()

    # Ajuste o caminho conforme onde a função é importada na rota.
    monkeypatch.setattr("app.routers.files.upload_imagem", fake_upload_imagem)

    # Sobrescreve a dependência get_current_user para garantir a permissão necessária
    async def fake_get_current_user():
        return {"id": 1, "permissoes": ["book.create"]}
    monkeypatch.setattr("app.routers.files.get_current_user", fake_get_current_user)

    # Simula o envio do arquivo (conteúdo dummy)
    file_content = b"conteudo_imagem_dummy"
    files = {"file": ("dummy.png", file_content, "image/png")}

    # Realiza a requisição para a rota /images/book_cover com o book_id na query
    response = await client.post("/images/book_cover?book_id=1", files=files, headers=admin_auth_headers)
    
    # Verifica se a resposta foi 200 OK
    assert response.status_code == 200
    data = response.json()

    # Verifica se a URL da imagem foi atualizada conforme o fake_upload_imagem
    assert data.get("image_url") == "http://images_service:8000/files/book_cover/dummy.png"