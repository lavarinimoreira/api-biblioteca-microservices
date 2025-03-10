#!/usr/bin/env python3
"""=============================================------------------
/api_biblioteca/services/scripts/_populate_db.py
================================================------------------

Este script realiza a inserção de dados iniciais no banco de dados.

Certifique-se de já ter realizado a migração das tabelas iniciais.

----------------------------------------------------------------"""

import asyncio

async def main():
    from app.services.scripts.populate_policy_group import insert_policy_groups
    from app.services.scripts.populate_permissions import insert_permissions
    from app.services.scripts.populate_policy_group_permission import insert_policy_group_permissions
    from app.services.scripts.populate_admin import create_admin

    await insert_policy_groups()
    await insert_permissions()
    await insert_policy_group_permissions()
    await create_admin()

if __name__ == '__main__':
    asyncio.run(main())

