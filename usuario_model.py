from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.base import Base


class UsuarioModel(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_completo = Column(String(256), nullable=True)
    email = Column(String(256), index=True, nullable=False, unique=True)
    senha = Column(String(256), nullable=False)

    cartoes = relationship(
        "CartaoModel",
        cascade="all, delete-orphan",
        back_populates="usuario",
        uselist=True,
        lazy="joined"
    )
