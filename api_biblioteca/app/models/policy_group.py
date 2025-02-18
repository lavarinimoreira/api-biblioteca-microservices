from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.policy_group_permission import grupo_politica_permissao



class GrupoPolitica(Base):
    __tablename__ = 'grupo_politica'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False, unique=True)
    data_criacao = Column(DateTime, default=func.now())
    data_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())

    usuarios = relationship("Usuario", back_populates="grupo_politica_rel")
    permissoes = relationship("Permissao", secondary=grupo_politica_permissao, back_populates="grupos_politica")