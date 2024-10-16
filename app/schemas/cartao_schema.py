import unicodedata
from fastapi import HTTPException, status
from pydantic import BaseModel, field_validator, Field
from uuid import UUID
from typing import List, Optional
from pytz import timezone
from app.models.cartao_model import CartaoModel, StatusEnum


class CriarCartao(BaseModel):
    titular_cartao: str = Field(title="Nome completo do titular",
                                 description="Nome completo do titular do cartão.")
    cpf_titular: str = Field(title="CPF do titular",
                             description="CPF do titular do cartão.")
    endereco: str = Field(title="Endereço do titular",
                          description="Endereço completo do titular do cartão.")

    @field_validator("endereco", mode="before")
    def validator_endereco(cls, v):
        if not v.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Endereço é um campo obrigatório e não pode ser vazio.")
        v = " ".join(v.split())
        return ''.join(
            c for c in unicodedata.normalize('NFD', v) if unicodedata.category(c) != 'Mn'
        )

    @field_validator("titular_cartao", mode="before")
    def validator_titular_cartao(cls, v):
        if not v.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Nome titular é um campo obrigatório e não pode ser vazio.")
        v = " ".join(v.split())
        if not all(parte.isalpha() or parte.isspace() for parte in v):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="O nome do titular deve ser composto apenas por letras.")
        return ''.join(
            c for c in unicodedata.normalize('NFD', v) if unicodedata.category(c) != 'Mn'
        )

    @field_validator('cpf_titular', mode="before")
    def validar_cpf(cls, v):
        if not v.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="CPF é um campo obrigatório e não pode ser vazio.")
        if not v.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O CPF deve conter apenas números.")
        if len(v) != 11:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O CPF deve conter exatamente 11 dígitos.")
        return v

    class Config:
        from_attributes = True


class CartaoCriadoResponse(CriarCartao):
    status: StatusEnum

    @classmethod
    def from_model(cls, cartao: CartaoModel) -> "CartaoCriadoResponse":
        return cls(
            titular_cartao=cartao.titular_cartao,
            cpf_titular=cartao.cpf_titular,
            endereco=cartao.endereco,
            status=cartao.status
        )


class CartaoResponseWrapper(BaseModel):
    status_code: int
    message: str
    data: CartaoCriadoResponse


class CartaoResponse(BaseModel):
    uuid: UUID
    titular_cartao: str
    cpf_titular: str
    status: StatusEnum
    endereco: str
    numero_cartao: str
    cvv: str
    expiracao: str
    data_criacao: str

    class Config:
        from_attributes = True

    @classmethod
    def from_model(cls, cartao: CartaoModel) -> "CartaoResponse":
        return cls(
            uuid=cartao.uuid,
            titular_cartao=cartao.titular_cartao,
            cpf_titular=cartao.cpf_titular,
            status=cartao.status,
            endereco=cartao.endereco,
            numero_cartao=cartao.numero_cartao_descriptografado,
            cvv=cartao.cvv_descriptografado,
            expiracao=cartao.expiracao.strftime("%m/%Y"),
            data_criacao=cartao.data_criacao.astimezone(timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S')
        )


class CartoesPorCpfResponse(BaseModel):
    cartoes: List[CartaoResponse]


class CartoesPorCpfWrapper(BaseModel):
    status_code: int
    message: str
    data: CartoesPorCpfResponse


class TodosOsCartoesResponse(BaseModel):
    cartoes: List[CartaoResponse]


class TodosOsCartoesWrapper(BaseModel):
    status_code: int
    message: str
    data: TodosOsCartoesResponse


class CartaoUpdate(BaseModel):
    titular_cartao: Optional[str] = None
    endereco: Optional[str] = None
    status: Optional[StatusEnum] = None

    @field_validator("endereco", mode="before")
    def validator_endereco(cls, v):
        if v is not None:
            if not v.strip():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Endereço inválido. O endereço não pode ser vazio.")
            v = " ".join(v.split())
            return ''.join(
                c for c in unicodedata.normalize('NFD', v) if unicodedata.category(c) != 'Mn'
            )
        return v

    @field_validator("titular_cartao", mode="before")
    def validator_titular_cartao(cls, v):
        if v is not None:
            if not v.strip():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Nome inválido. O nome do titular não pode ser vazio.")
            v = " ".join(v.split())
            if not all(parte.isalpha() or parte.isspace() for parte in v):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Nome inválido. O nome do titular deve ser composto apenas por letras.")
            return ''.join(
                c for c in unicodedata.normalize('NFD', v) if unicodedata.category(c) != 'Mn'
            )
        return v

    @classmethod
    def from_model(cls, cartao_atualizado: CartaoModel) -> "CartaoUpdate":
        return cls(
            uuid=cartao_atualizado.uuid,
            titular_cartao=cartao_atualizado.titular_cartao,
            cpf_titular=cartao_atualizado.cpf_titular,
            status=cartao_atualizado.status,
            endereco=cartao_atualizado.endereco,
            numero_cartao=cartao_atualizado.numero_cartao_descriptografado,
            cvv=cartao_atualizado.cvv_descriptografado,
            expiracao=cartao_atualizado.expiracao.strftime("%m/%Y"),
            data_criacao=cartao_atualizado.data_criacao.astimezone(timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S')
        )

    class Config:
        from_attributes = True


class CartaoUpdateWrapper(BaseModel):
    status_code: int
    message: str
    data: CartaoUpdate
