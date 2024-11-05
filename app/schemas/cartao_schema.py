import unicodedata
from fastapi import HTTPException, status
from pydantic import BaseModel, field_validator, Field
from uuid import UUID
from typing import List, Optional
from pytz import timezone
from app.models.cartao_model import CartaoModel, StatusEnum


class CriarCartao(BaseModel):
    titular_cartao: str = Field(title="Nome completo do titular",
                                description="Nome completo do titular do cartão.",
                                examples=["JOAO DA SILVA"])
    cpf_titular: str = Field(title="CPF do titular",
                             description="CPF do titular do cartão.",
                             examples=["12345678912"])
    endereco: str = Field(title="Endereço do titular",
                          description="Endereço completo do titular do cartão.",
                          examples=["RUA DA FELICIDADE, BAIRRO ALEGRIA"])

    @field_validator("endereco", mode="before")
    def validator_endereco(cls, v):
        if not v.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Endereço é um campo obrigatório e não pode ser uma string vazia.")
        v = " ".join(v.split())
        return ''.join(
            c for c in unicodedata.normalize('NFD', v) if unicodedata.category(c) != 'Mn'
        )

    @field_validator("titular_cartao", mode="before")
    def validator_titular_cartao(cls, v):
        if not v.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Nome titular é um campo obrigatório e não pode ser uma string vazia.")
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
                                detail="CPF é um campo obrigatório e não pode ser uma string vazia.")
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
    status: StatusEnum = Field(title="Status do cartão",
                               description="Status atual do cartão.")
    token: str = Field(title="Token de acesso",
                       description="Token de acesso do CPF vinculado ao cartão.")

    @classmethod
    def from_model(cls, cartao: CartaoModel) -> "CartaoCriadoResponse":
        return cls(
            titular_cartao=cartao.titular_cartao,
            cpf_titular=cartao.cpf_titular,
            endereco=cartao.endereco,
            status=cartao.status,
            token=cartao.hash_token_descriptografado
        )


class CartaoResponseWrapper(BaseModel):
    status_code: int = Field(title="Código de status",
                             description="Código HTTP indicando o status da operação.")
    message: str = Field(title="Mensagem de resposta",
                         description="Mensagem que descreve o resultado da operação.")
    data: CartaoCriadoResponse = Field(title="Dados do cartão criado",
                                       description="Informações sobre o cartão que foi criado.")


class CartaoResponse(BaseModel):
    uuid: UUID = Field(title="UUID do cartão",
                       description="Identificador único do cartão.")
    titular_cartao: str = Field(title="Nome do titular do cartão",
                                description="Nome completo do titular do cartão.")
    cpf_titular: str = Field(title="CPF do titular",
                             description="CPF do titular do cartão.")
    status: StatusEnum = Field(title="Status do cartão",
                               description="Status atual do cartão.")
    endereco: str = Field(title="Endereço do titular",
                          description="Endereço completo do titular do cartão.")
    saldo: float = Field(title="Saldo do cartão",
                          description="Saldo atual do cartão.")
    numero_cartao: str = Field(title="Número do cartão",
                               description="Número do cartão de crédito.")
    cvv: str = Field(title="CVV do cartão",
                     description="Código de verificação do cartão.")
    expiracao: str = Field(title="Data de expiração",
                           description="Data de expiração do cartão no formato MM/AAAA.")
    data_criacao: str = Field(title="Data de criação",
                              description="Data e hora em que o cartão foi criado, no formato dd/MM/yyyy HH:mm:ss.")
    token: str = Field(title="Token de acesso",
                       description="Token de acesso do CPF vinculado ao cartão.")

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
            saldo=cartao.saldo,
            numero_cartao=cartao.numero_cartao_descriptografado,
            cvv=cartao.cvv_descriptografado,
            expiracao=cartao.expiracao.strftime("%m/%Y"),
            data_criacao=cartao.data_criacao.astimezone(timezone('America/Sao_Paulo')).strftime('%d/%m/%Y %H:%M:%S'),
            token=cartao.hash_token_descriptografado
        )


class CartoesPorCpfResponse(BaseModel):
    cartoes: List[CartaoResponse] = Field(title="Lista de cartões",
                                          description="Lista de cartões associados ao CPF fornecido.")


class CartoesPorCpfWrapper(BaseModel):
    status_code: int = Field(title="Código de status",
                             description="Código HTTP indicando o status da operação.")
    message: str = Field(title="Mensagem de resposta",
                         description="Mensagem que descreve o resultado da operação.")
    data: CartoesPorCpfResponse = Field(title="Dados dos cartões",
                                        description="Informações sobre os cartões associados ao CPF.")


class CartaoUpdate(BaseModel):
    titular_cartao: Optional[str] = Field(None,
                                          title="Nome do titular do cartão",
                                          description="Nome completo do titular do cartão.",
                                          examples=['JOAO DA SILVA'])
    endereco: Optional[str] = Field(None,
                                    title="Endereço do titular",
                                    description="Endereço completo do titular do cartão.",
                                    examples=['12345678912'])
    status: Optional[StatusEnum] = Field(None,
                                         title="Status do cartão",
                                         description="Status atual do cartão.",
                                         examples=["RUA DA FELICIDADE, BAIRRO ALEGRIA"]),

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
                                    detail="O nome do titular não pode ser uma string vazia.")
            v = " ".join(v.split())
            if not all(parte.isalpha() or parte.isspace() for parte in v):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="O nome do titular deve ser composto apenas por letras.")
            return ''.join(
                c for c in unicodedata.normalize('NFD', v) if unicodedata.category(c) != 'Mn'
            )
        return v

    class Config:
        from_attributes = True


class CartaoUpdateWrapper(BaseModel):
    status_code: int = Field(title="Código de status",
                             description="Código HTTP indicando o status da operação.")
    message: str = Field(title="Mensagem de resposta",
                         description="Mensagem que descreve o resultado da operação.")
    data: CartaoResponse = Field(title="Dados do cartão atualizado",
                                 description="Informações sobre o cartão que foi atualizado.")


class CartaoTransferir(BaseModel):
    uuid_pagante: UUID = Field(title="UUID do pagante",
                               description="Identificador do pagante.")
    uuid_recebente: UUID = Field(title="UUID do recebente",
                                 description="Identificador do recebente.")
    valor: float = Field(title="Valor a ser transferido",
                         description="Valor a ser transferido para outro cartão.")


class CartaoTransferirWrapper(BaseModel):
    status_code: int = Field(title="Código de status",
                             description="Código HTTP indicando o status da operação.")
    message: str = Field(title="Mensagem de resposta",
                         description="Mensagem que descreve o resultado da operação.")
    data: CartaoResponse = Field(title="Dados do cartão atualizado",
                                 description="Informações sobre o cartão que teve o saldo atualizado.")


class CartaoRecarga(BaseModel):
    valor: float = Field(title="Valor da recarga",
                         description="Valor da recarga a ser feito no cartão do titular.")

    class Config:
        from_attributes = True


class CartaoRecargaWrapper(BaseModel):
    status_code: int = Field(title="Código de status",
                             description="Código HTTP indicando o status da operação.")
    message: str = Field(title="Mensagem de resposta",
                         description="Mensagem que descreve o resultado da operação.")
    data: CartaoResponse = Field(title="Dados do cartão atualizado",
                                 description="Informações sobre o cartão que teve o saldo atualizado.")
