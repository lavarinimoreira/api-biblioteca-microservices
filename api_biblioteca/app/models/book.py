from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func




class Livro(Base):
    __tablename__ = 'livro'
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(200), nullable=False)
    autor = Column(String(100), nullable=False)
    genero = Column(String(50))
    editora = Column(String(100))
    ano_publicacao = Column(Integer)
    numero_paginas = Column(Integer)
    quantidade_disponivel = Column(Integer, nullable=False)
    isbn = Column(String(20), unique=True, nullable=False)
    data_criacao = Column(DateTime, default=func.now())
    data_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())
    emprestimos = relationship("Emprestimo", back_populates="livro")
    image_url = Column(String, nullable=True) # Caminho da imagem