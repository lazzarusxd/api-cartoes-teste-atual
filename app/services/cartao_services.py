from uuid import UUID
from fastapi import status, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.cartao_model import CartaoModel
from app.database.base import get_session
from app.schemas.cartao_schema import (CriarCartao, CartaoResponse, CartaoCriadoResponse, CartoesPorCpfResponse,
                                       CartaoUpdate, CartaoUpdateResponse, CartaoTransferir, CartaoTransferirResponse)

class CartaoServices:

    def __init__(self, db: AsyncSession = Depends(get_session)):
        self.db = db

    async def solicitar_cartao(self, dados_cartao: CriarCartao) -> dict:
        try:
            query = await self.db.execute(
                select(CartaoModel).where(
                    and_(
                        CartaoModel.cpf_titular == dados_cartao.cpf_titular
                    )
                )
            )
            usuario_existente = query.scalars().all()

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

            await cartao.initialize()

            self.db.add(cartao)

            await self.db.commit()
            await self.db.refresh(cartao)

            return {
                "status_code": status.HTTP_201_CREATED,
                "message": "Cartão criado com sucesso.",
                "data": CartaoCriadoResponse.from_model(cartao)
            }

        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro ao criar cartão: {str(e)}"
            )

    async def listar_cartoes_por_cpf(self, cpf_titular: str) -> dict:
        query = await self.db.execute(
            select(CartaoModel).where(
                and_(CartaoModel.cpf_titular == cpf_titular)
            )
        )
        cartoes = query.scalars().all()

        if not cartoes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="O CPF informado não foi encontrado."
            )

        cartoes_response = [CartaoResponse.from_model(cartao) for cartao in cartoes]

        return {
            "status_code": status.HTTP_200_OK,
            "message": "Todos os cartões foram listados com sucesso.",
            "data": CartoesPorCpfResponse(cartoes=cartoes_response),
        }

    async def atualizar_info(self, dados_atualizados: CartaoUpdate, uuid: UUID) -> dict:
        query = await self.db.execute(
            select(CartaoModel).where(
                and_(
                    CartaoModel.uuid == uuid
                )
            )
        )
        cartao = query.scalars().first()

        if not cartao:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Cartão não encontrado, verifique o UUID.")

        atualizacoes_cartao = {}
        if dados_atualizados.titular_cartao is not None or dados_atualizados.endereco is not None:
            query_atualizar_cartoes = select(CartaoModel).where(
                and_(
                    CartaoModel.cpf_titular == cartao.cpf_titular,
                    CartaoModel.titular_cartao == cartao.titular_cartao
                )
            )
            result_cartoes = await self.db.execute(query_atualizar_cartoes)
            cartoes_para_atualizar = result_cartoes.scalars().all()

            if dados_atualizados.titular_cartao is not None:
                atualizacoes_cartao["titular_cartao"] = dados_atualizados.titular_cartao
                for cartao_atualizar in cartoes_para_atualizar:
                    cartao_atualizar.titular_cartao = dados_atualizados.titular_cartao

            if dados_atualizados.endereco is not None:
                atualizacoes_cartao["endereco"] = dados_atualizados.endereco
                for cartao_atualizar in cartoes_para_atualizar:
                    cartao_atualizar.endereco = dados_atualizados.endereco

        if dados_atualizados.status is not None:
            atualizacoes_cartao["status"] = dados_atualizados.status
            cartao.status = dados_atualizados.status

        if dados_atualizados.saldo is not None:
            atualizacoes_cartao["saldo"] = dados_atualizados.saldo
            cartao.saldo = dados_atualizados.saldo

        if not atualizacoes_cartao:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Erro. Não foram informados dados a serem atualizados.")

        try:
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Erro ao atualizar o cartão. Tente novamente mais tarde.")

        return {
            "status_code": status.HTTP_200_OK,
            "message": "Dados atualizados com sucesso.",
            "data": CartaoUpdateResponse.from_model(cartao)
        }


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
                "message": f"Foi enviado R${transferencia.valor:.2f} do cartão '{cartao.uuid}'"
                             f" para o cartão '{cartao2.uuid}.",
                "data": CartaoTransferirResponse.from_model(cartao2)
            }
