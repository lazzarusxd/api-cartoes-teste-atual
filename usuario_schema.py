from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator
from app.schemas.cartao_schema import CartaoResponse
import re


class Usuario(BaseModel):
    nome_completo: str
    email: EmailStr

    class Config:
        from_attributes = True

    @field_validator('nome_completo', mode='before')
    def validator_nome_completo(cls, v):
        if not v or v.strip() == "":
            raise ValueError("O campo 'nome_completo' não pode ser vazio.")
        if not re.match('^[A-Za-z\s]+$', v):
            raise ValueError("O campo 'nome_completo' deve conter apenas letras e espaços.")
        return v


class UsuarioCriarSenha(Usuario):
    senha: str


class UsuarioCartoes(Usuario):
    cartoes: Optional[List[CartaoResponse]] = None


class UsuarioAtualizar(Usuario):
    nome_completo: Optional[str] = None
    email: Optional[str] = None
    senha: Optional[str] = None
