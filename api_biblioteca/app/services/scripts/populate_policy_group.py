"""
Este script realiza a inserção de dados básicos no Grupo de Políticas.
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import AsyncSessionLocal
from app.models.policy_group import GrupoPolitica
from app.models.__all_models import Base

async def insert_policy_groups():
    async with AsyncSessionLocal() as db:
        grupos = ["admin", "cliente"]

        for grupo in grupos:
            # Verifica se o grupo já existe
            result = await db.execute(select(GrupoPolitica).where(GrupoPolitica.nome == grupo))
            exists = result.scalar_one_or_none()

            if not exists:
                novo_grupo = GrupoPolitica(nome=grupo)
                db.add(novo_grupo)
                print(f"----> Grupo de política '{grupo}' criado.")

        await db.commit()

if __name__ == "__main__":
    asyncio.run(insert_policy_groups())

