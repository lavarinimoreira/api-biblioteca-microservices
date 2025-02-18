"""
  Este script realiza a inserção dos relacionamentos entre Grupo de Políticas e Permissões.

  Certifique-se de ter as tabelas "GrupoPolitica" e "Permissao" já devidamente populadas.
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import AsyncSessionLocal
from app.models.policy_group import GrupoPolitica
from app.models.permission import Permissao
from app.models.policy_group_permission import grupo_politica_permissao
from app.models.__all_models import Base

# Mapeamento das permissões por grupo
permissoes_admin = [
    "book.create", "book.update", "book.delete", "book.read_by_title",
    "book.read_by_author", "book.read_by_genre",
    "admin.create", "admin.read", "admin.update", "admin.delete",
    "client.create", "client.read", "client.read_by_id", "client.update", "client.delete",
    "policy_group.create", "policy_group.read", "policy_group.update", "policy_group.update_user", "policy_group.delete",
    "policy_group_permission.create", "policy_group_permission.read", "policy_group_permission.update", "policy_group_permission.delete",
    "loan.create", "loan.renew", "loan.read_by_client"
]
permissoes_cliente = [
    "book.read_by_title", "book.read_by_author", "book.read_by_genre",
    "loan.read_by_client", "client.update_self"
]

async def insert_policy_group_permissions():
    async with AsyncSessionLocal() as db:
        
        # Associa permissões ao grupo correspondente
        async def associar_permissoes(grupo_nome, permissoes):
            result_grupo = await db.execute(select(GrupoPolitica).where(GrupoPolitica.nome == grupo_nome))
            grupo = result_grupo.scalar_one_or_none()

            if not grupo:
                print(f"Grupo de política '{grupo_nome}' não encontrado. Certifique-se de rodar o script de criação de grupos antes.")
                return
            
            for namespace in permissoes:
                result_permissao = await db.execute(select(Permissao).where(Permissao.namespace == namespace))
                permissao = result_permissao.scalar_one_or_none()

                if not permissao:
                    print(f"Permissão '{namespace}' não encontrada. Certifique-se de rodar o script de inserção de permissões antes.")
                    continue

                # Verifica se a relação já existe
                result_relacao = await db.execute(select(grupo_politica_permissao).where(
                    (grupo_politica_permissao.c.grupo_politica_nome == grupo_nome) &
                    (grupo_politica_permissao.c.permissao_namespace == namespace)
                ))
                relacao_existente = result_relacao.fetchone()

                if not relacao_existente:
                    stmt = grupo_politica_permissao.insert().values(
                        grupo_politica_nome=grupo_nome,
                        permissao_namespace=namespace
                    )
                    await db.execute(stmt)
                    print(f"Permissão '{namespace}' associada ao grupo '{grupo_nome}'.")

        # Executa a associação para cada grupo
        await associar_permissoes("admin", permissoes_admin)
        await associar_permissoes("cliente", permissoes_cliente)

        await db.commit()

if __name__ == "__main__":
    asyncio.run(insert_policy_group_permissions())
