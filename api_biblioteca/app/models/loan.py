# Tabelas
from app.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Emprestimo(Base):
    __tablename__ = 'emprestimo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, ForeignKey('usuario.id'), nullable=False)
    livro_id = Column(Integer, ForeignKey('livro.id'), nullable=False)
    data_emprestimo = Column(DateTime, default=func.now())
    data_devolucao = Column(DateTime)
    numero_renovacoes = Column(Integer, default=0)
    status = Column(String(20), nullable=False)
    usuario = relationship("Usuario", back_populates="emprestimos")
    livro = relationship("Livro", back_populates="emprestimos")