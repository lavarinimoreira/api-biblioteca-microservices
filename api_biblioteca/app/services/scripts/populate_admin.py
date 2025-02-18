"""
Este script realiza a inserção de um administrador ao banco de dados.

Certifique-se de ter as permissões e os grupos de política devidamente já povoados.
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import AsyncSessionLocal
from app.models.user import Usuario
from app.services.security import bcrypt_context  # Importa o contexto para hash de senha
from app.models.__all_models import Base

async def create_admin():
    async with AsyncSessionLocal() as db:
        admin_email = "admin@biblioteca.com"
        admin_nome = "Administrador"
        admin_senha = "admin123"  # ALTERE ESTA SENHA APÓS CRIAÇÃO!
        grupo_politica = "admin"

        # Verifica se já existe um admin com este e-mail
        result = await db.execute(select(Usuario).where(Usuario.email == admin_email))
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            print("Um usuário admin já existe. Nenhuma ação foi tomada.")
            return

        # Criando o novo admin com senha hash
        novo_admin = Usuario(
            nome=admin_nome,
            email=admin_email,
            telefone="(00) 00000-0000",
            endereco_completo="Endereço não especificado",
            senha_hash=bcrypt_context.hash(admin_senha),
            grupo_politica=grupo_politica
        )

        db.add(novo_admin)
        await db.commit()
        print(f"----> Usuário admin criado com sucesso!\nEmail: {admin_email}\nAltere esta senha após a criação: {admin_senha}")

if __name__ == "__main__":
    asyncio.run(create_admin())
