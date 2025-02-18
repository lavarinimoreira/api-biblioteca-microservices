from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.policy_group_permission import grupo_politica_permissao


class Permissao(Base):
    __tablename__ = 'permissao'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False, unique=True)
    descricao = Column(String(255))
    namespace = Column(String(100), nullable=False, unique=True)
    data_criacao = Column(DateTime, default=func.now())
    data_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())

    grupos_politica = relationship("GrupoPolitica", secondary=grupo_politica_permissao, back_populates="permissoes")