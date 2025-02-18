from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, column_property
from sqlalchemy.sql import func


class Usuario(Base):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    telefone = Column(String(15))
    endereco_completo = Column(String(200))
    senha_hash = Column(String(255), nullable=False)
    profile_picture_url = Column(String, nullable=True)  # Caminho da foto de perfil
    # Atualização do grupo_política para string, já que o nome é uma chave candidata da tabela GrupoPolitica
    grupo_politica = Column(String(100), ForeignKey('grupo_politica.nome'), nullable=False, default="cliente")

    data_criacao = Column(DateTime, default=func.now())
    data_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())

    grupo_politica_rel = relationship("GrupoPolitica", back_populates="usuarios")
    emprestimos = relationship("Emprestimo", back_populates="usuario")
