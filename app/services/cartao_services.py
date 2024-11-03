from uuid import UUID
from fastapi import APIRouter, status, Depends, HTTPException, Path
from sqlalchemy import and_
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import criar_token_acesso
from app.models.cartao_model import CartaoModel
from app.database.base import get_session
from app.api.v1.endpoints.responses.cartao_responses import Responses
from app.core.deps import get_current_user_cpf
from app.schemas.cartao_schema import (CriarCartao, CartaoResponse, CartaoCriadoResponse, CartaoResponseWrapper,
                                       CartoesPorCpfWrapper, CartoesPorCpfResponse,
                                       CartaoUpdate, CartaoUpdateResponse, CartaoUpdateWrapper,
                                       CartaoTransferir, CartaoTransferirResponse,
                                       CartaoTransferirWrapper)

class CartaoServices:

    def __init__(self, db: AsyncSession = Depends(get_session)):
        self.db = db

    async def solicitar_cartao(self,
                               dados_cartao: CriarCartao) -> dict:

        try:
            result = await self.db.execute(
                select(CartaoModel).where(
                    and_(
                        CartaoModel.cpf_titular == dados_cartao.cpf_titular
                    )
                )
            )
            usuario_existente = result.scalars().all()

            for usuario in usuario_existente:
                if usuario.titular_cartao.upper() != dados_cartao.titular_cartao.upper():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="CPF já cadastrado para um titular diferente."
                    )

            cartao = CartaoModel(
                titular_cartao=dados_cartao.titular_cartao.upper(),
                cpf_titular=dados_cartao.cpf_titular,
                endereco=dados_cartao.endereco.upper()
            )

            token = criar_token_acesso(dados_cartao.cpf_titular)

            await cartao.initialize()

            self.db.add(cartao)

            await self.db.commit()
            await self.db.refresh(cartao)

            return {
                "status_code": status.HTTP_201_CREATED,
                "message": "Cartão criado com sucesso.",
                "data": CartaoCriadoResponse.from_model(cartao, token)
            }

        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro ao criar cartão: {str(e)}"
            )

    async def transferir_saldo(self, transferencia: CartaoTransferir) -> dict:

        query = select(CartaoModel).where(
            and_(
                CartaoModel.uuid == transferencia.uuid_pagador,
            )
        )
        result = await self.db.execute(query)
        cartao = result.scalars().first()

        if cartao is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="O UUID do pagador informado não pertence a nenhum cartão.")

        if transferencia.valor > cartao.saldo:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail=f"Saldo insuficiente, o saldo é de R${cartao.saldo:.2f} "
                                       f"e a transferência solicitada foi de R${transferencia.valor:.2f}.")

        saldo_atualizado = cartao.saldo - transferencia.valor
        cartao.saldo = saldo_atualizado

        query2 = select(CartaoModel).where(
            and_(
                CartaoModel.uuid == transferencia.uuid_recebedor
            )
        )
        result2 = await self.db.execute(query2)
        cartao2 = result2.scalars().first()

        if cartao2 is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="O UUID do recebedor informado não pertence a nenhum cartão.")

        cartao2.saldo += transferencia.valor

        try:
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Erro ao atualizar o cartão. Tente novamente mais tarde.")

        return {
            "status_code": status.HTTP_200_OK,
            "message": f"Foi enviado R${transferencia.valor} do cartão '{cartao.uuid}'"
                         f" para o cartão '{cartao2.uuid}.",
            "data": CartaoTransferirResponse.from_model(cartao2)
        }
