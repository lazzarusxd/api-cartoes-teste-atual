from uuid import UUID

from fastapi import APIRouter, status, Depends, HTTPException, Path
from sqlalchemy import and_
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.cartao_model import CartaoModel
from app.database.base import get_session
from app.api.v1.endpoints.responses.cartao_responses import Response
from app.schemas.cartao_schema import (CriarCartao, CartaoResponse,
                                       CartaoCriadoResponse, CartaoResponseWrapper,
                                       TodosOsCartoesResponse, TodosOsCartoesWrapper,
                                       CartoesPorCpfWrapper, CartoesPorCpfResponse,
                                       CartaoUpdate, CartaoUpdateWrapper)

router = APIRouter()


@router.post("/solicitar_cartao",
             response_model=CartaoResponseWrapper,
             status_code=status.HTTP_201_CREATED,
             summary="Solicitar Cartão",
             description="Gera um novo cartão para o usuário com base nas informações fornecidas.",
             responses={
                 **Response.sucesso_response,
                 **Response.erro_validacao_response
             })
async def post_solicitar_cartao(dados_cartao: CriarCartao,
                                db: AsyncSession =
                                Depends(get_session)) -> CartaoResponseWrapper:
    try:
        result = await db.execute(
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

        await cartao.initialize()

        db.add(cartao)

        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro ao salvar cartão no banco."
            )

        await db.refresh(cartao)

        response = CartaoCriadoResponse.from_model(cartao)

        return CartaoResponseWrapper(status_code=status.HTTP_201_CREATED,
                                     message="Cartão criado com sucesso.",
                                     data=response)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao criar cartão: {str(e)}"
        )


@router.get("/listar_cartoes/todos",
            response_model=TodosOsCartoesWrapper,
            status_code=status.HTTP_200_OK)
async def get_cartoes(db: AsyncSession = Depends(get_session)) -> TodosOsCartoesWrapper:
    query = select(CartaoModel).filter_by()
    result = await db.execute(query)
    cartoes = result.scalars().all()

    cartoes_response = [CartaoResponse.from_model(cartao) for cartao in cartoes]

    return TodosOsCartoesWrapper(status_code=status.HTTP_200_OK,
                                 message="Todos os cartões foram listados com sucesso.",
                                 data=TodosOsCartoesResponse(cartoes=cartoes_response))


@router.get("/listar_cartoes/cpf/{cpf_titular}",
            response_model=CartoesPorCpfWrapper,
            status_code=status.HTTP_200_OK)
async def get_cartoes_por_cpf(cpf_titular: str = Path(title="CPF do titular",
                                                      description="CPF do titular do cartão.",
                                                      example="29348934029"),
                              db: AsyncSession = Depends(get_session)) -> CartoesPorCpfWrapper:
    query = select(CartaoModel).where(
        and_(
            CartaoModel.cpf_titular == cpf_titular
        )
    )
    result = await db.execute(query)
    cartoes = result.scalars().all()

    if not cartoes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="O UUID informado não foi encontrado.")
    cartoes_response = [CartaoResponse.from_model(cartao) for cartao in cartoes]

    return CartoesPorCpfWrapper(status_code=status.HTTP_200_OK,
                                 message="Todos os cartões foram listados com sucesso.",
                                 data=CartoesPorCpfResponse(cartoes=cartoes_response))


@router.put("/atualizar_info/{uuid}",
            response_model=CartaoUpdateWrapper,
            status_code=status.HTTP_200_OK)
async def atualizar_informacoes(dados_atualizados: CartaoUpdate,
                                uuid: UUID = Path(title="UUID do cartão.",
                                                 description="UUID do cartão a ser atualizado."),
                                db: AsyncSession = Depends(get_session)) -> CartaoUpdateWrapper:
    query = select(CartaoModel).where(
        and_(
            CartaoModel.uuid == uuid
        )
    )
    result = await db.execute(query)
    cartao = result.scalars().first()

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
        result_cartoes = await db.execute(query_atualizar_cartoes)
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

    if not atualizacoes_cartao:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Erro. Não foi informado nenhum dado para atualizar.")

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Erro ao atualizar o cartão. Tente novamente mais tarde.")

    return CartaoUpdateWrapper(status_code=status.HTTP_200_OK,
                               message="Dados atualizados com sucesso.",
                               data=atualizacoes_cartao)
