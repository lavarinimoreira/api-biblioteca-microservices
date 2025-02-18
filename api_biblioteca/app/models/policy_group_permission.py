from app.database import Base
from sqlalchemy import Column, String, ForeignKey, Table

# Tabela de associação para o relacionamento muitos-para-muitos entre GrupoPolitica e Permissao
grupo_politica_permissao = Table(
    'grupo_politica_permissao',
    Base.metadata,
    # Como os nomes de grupo_politica.nome e permissao.namespace são chaves candidatas, podem ser utilizadas
    # aqui como chaves estrangeiras para melhor legibilidade do admin durante os updates.
    Column('grupo_politica_nome', String(100), ForeignKey('grupo_politica.nome'), primary_key=True),
    Column('permissao_namespace', String(100), ForeignKey('permissao.namespace'), primary_key=True)
)
