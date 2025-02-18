"""
Este script realiza a inserção de dados básicos relacionados às Permissoes.
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import AsyncSessionLocal
from app.models.permission import Permissao
from app.models.__all_models import Base

permissoes = [
    # Permissões para Livros
    {"nome": "Criar Livro", "namespace": "book.create", "descricao": "Permite criar um novo livro"},
    {"nome": "Listar Livro por Título", "namespace": "book.read_by_title", "descricao": "Permite verificar um livro pelo título"},
    {"nome": "Listar Livro por Autor", "namespace": "book.read_by_author", "descricao": "Permite verificar os livros de um determinado autor"},
    {"nome": "Listar Livro por Gênero", "namespace": "book.read_by_genre", "descricao": "Permite verificar os livros de determinado gênero"},
    {"nome": "Editar Livro", "namespace": "book.update", "descricao": "Permite editar um livro existente"},
    {"nome": "Deletar Livro", "namespace": "book.delete", "descricao": "Permite remover um livro"},


    {"nome": "Criar Admin", "namespace": "admin.create", "descricao": "Permite criar um novo administrador"},
    {"nome": "Listar Admins", "namespace": "admin.read", "descricao": "Permite verificar os administradores registrados"},
    {"nome": "Editar Admin", "namespace": "admin.update", "descricao": "Permite editar um administrador"},
    {"nome": "Deletar Admin", "namespace": "admin.delete", "descricao": "Permite deletar um administrador"},
    
 
    {"nome": "Criar Cliente", "namespace": "client.create", "descricao": "Permite criar um cliente"},
    {"nome": "Editar Cliente", "namespace": "client.update", "descricao": "Permite editar um cliente"},
    {"nome": "Listar Clientes", "namespace": "client.read", "descricao": "Permite visualizar todos os clientes registrados"},
    {"nome": "Buscar Cliente por ID", "namespace": "client.read_by_id", "descricao": "Permite procurar por um cliente"},
    {"nome": "Deletar Cliente", "namespace": "client.delete", "descricao": "Permite deletar um cliente"},
    {"nome": "Editar Próprio Perfil", "namespace": "client.update_self", "descricao": "Permite ao cliente editar seus próprios dados"},

    # Permissões para Grupos de Política
    {"nome": "Criar Grupo de Política", "namespace": "policy_group.create", "descricao": "Permite criar um grupo de políticas"},
    {"nome": "Listar Grupos de Política", "namespace": "policy_group.read", "descricao": "Permite visualizar os grupos de políticas"},
    {"nome": "Editar Grupo de Política", "namespace": "policy_group.update", "descricao": "Permite editar um grupo de política"},
    {"nome": "Alterar Grupo de Política do Usuário", "namespace": "policy_group.update_user", "descricao": "Permite editar o grupo de políticas de um usuário"},
    {"nome": "Deletar Grupo de Política", "namespace": "policy_group.delete", "descricao": "Permite deletar um grupo de políticas"},

    # Permissões para Gestão de Permissões
    {"nome": "Listar Permissões", "namespace": "permission.read", "descricao": "Permite a visualização das permissões"},

    # Associações entre Grupos de Política e Permissões
    {"nome": "Criar Associação entre GP e Permissão", "namespace": "policy_group_permission.create", "descricao": "Cria uma associação entre Permissão e Grupo de Política"},
    {"nome": "Listar Associações entre GP e Permissão", "namespace": "policy_group_permission.read", "descricao": "Lista as associações dos Grupo de Políticas e Permissões"},
    {"nome": "Editar Associação entre GP e Permissão", "namespace": "policy_group_permission.update", "descricao": "Edita uma associação entre Permissão e Grupo de Política"},
    {"nome": "Deletar Associação entre GP e Permissão", "namespace": "policy_group_permission.delete", "descricao": "Exclui uma associação entre Permissão e Grupo de Política"},

    # Permissões para Empréstimos
    {"nome": "Registrar Empréstimo", "namespace": "loan.create", "descricao": "Permite a criação de um novo empréstimo"},
    {"nome": "Renovar Empréstimo", "namespace": "loan.renew", "descricao": "Permite a renovação de um empréstimo"},
    {"nome": "Listar Empréstimos do Cliente", "namespace": "loan.read_by_client", "descricao": "Permite visualizar a lista de empréstimos de um cliente"},
]

async def insert_permissions():
    async with AsyncSessionLocal() as db:
        # Lista de permissões iniciais
        
        for perm in permissoes:
            result = await db.execute(select(Permissao).where(Permissao.namespace == perm["namespace"]))
            exists = result.scalar_one_or_none()

            if not exists:
                nova_permissao = Permissao(**perm)
                db.add(nova_permissao)
                print(f"----> Permissão '{perm['nome']}' criada.")

        await db.commit()

if __name__ == "__main__":
    asyncio.run(insert_permissions())
