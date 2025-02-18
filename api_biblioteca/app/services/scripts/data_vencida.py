import asyncio
from datetime import datetime, timedelta

from app.database import AsyncSessionLocal, engine, Base
from app.models.book import Livro
from app.models.loan import Emprestimo
from app.models.__all_models import Base

async def main():

    # Cria uma sessão assíncrona para interagir com o BD
    async with AsyncSessionLocal() as session:
        # 1. Cria e adiciona um novo livro
        novo_livro = Livro(
            titulo="Livro de Teste",
            autor="Autor Teste",
            genero="Ficção",
            editora="Editora Teste",
            ano_publicacao=2020,
            numero_paginas=300,
            quantidade_disponivel=5,
            isbn="1230567890723"  # Certifique-se de que o ISBN seja único no BD
        )
        session.add(novo_livro)
        await session.commit()            # Salva o livro e gera seu id
        await session.refresh(novo_livro)   # Atualiza o objeto com os dados do BD

        print(f"Livro criado com ID: {novo_livro.id}")

        # 2. Cria um empréstimo para esse livro com data_devolucao atrasada (8 dias atrás)
        data_devolucao_atrasada = datetime.now() - timedelta(days=8)
        novo_emprestimo = Emprestimo(
            usuario_id=1,  # Usuário já existente no BD
            livro_id=novo_livro.id,
            data_emprestimo=datetime.now(),
            data_devolucao=data_devolucao_atrasada,
            status="Ativo"
        )
        session.add(novo_emprestimo)
        await session.commit()

        print(f"Empréstimo criado para o livro {novo_livro.id} com data_devolucao: {data_devolucao_atrasada}")

if __name__ == "__main__":
    asyncio.run(main())
