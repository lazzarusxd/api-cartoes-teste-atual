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
from app.services.cartao_services import CartaoServices
from app.schemas.cartao_schema import (CriarCartao, CartaoResponse, CartaoResponseWrapper,
                                       CartoesPorCpfWrapper, CartoesPorCpfResponse,
                                       CartaoUpdate, CartaoUpdateResponse, CartaoUpdateWrapper,
                                       CartaoTransferir, CartaoTransferirResponse,
                                       CartaoTransferirWrapper)

router = APIRouter()


@router.post("/solicitar_cartao",
             response_model=CartaoResponseWrapper,
             status_code=status.HTTP_201_CREATED,
             summary="Solicitar cartão",
             description="Gera um novo cartão para o usuário com base nas informações fornecidas.",
             responses={
                 **Responses.PostSolicitarCartao.sucesso_response,
                 **Responses.PostSolicitarCartao.erro_validacao_response
             })
async def post_solicitar_cartao(dados_cartao: CriarCartao,
                                cartao_services: CartaoServices = Depends()) -> CartaoResponseWrapper:

    cartao_response = await cartao_services.solicitar_cartao(dados_cartao)

    return CartaoResponseWrapper(
        status_code=cartao_response["status_code"],
        message=cartao_response["message"],
        data=cartao_response["data"]
    )


@router.get("/listar_cartoes/cpf/{cpf_titular}",
            response_model=CartoesPorCpfWrapper,
            status_code=status.HTTP_200_OK,
            summary="Listar cartões por CPF",
            description="Retorna todos os cartões vinculados ao CPF informado.",
            responses={
                **Responses.GetListarCartoesCpf.sucesso_response,
                **Responses.GetListarCartoesCpf.cpf_invalido_response,
                **Responses.GetListarCartoesCpf.erro_validacao_response
            })
async def get_cartoes_por_cpf(cpf_titular: str = Path(title="CPF do titular",
                                                      description="CPF do titular do cartão."),
                              db: AsyncSession = Depends(get_session),
                              _: str = Depends(get_current_user_cpf)) -> CartoesPorCpfWrapper:

    query = select(CartaoModel).where(
        and_(CartaoModel.cpf_titular == cpf_titular)
    )
    result = await db.execute(query)
    cartoes = result.scalars().all()

    if not cartoes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="O CPF informado não foi encontrado."
        )

    cartoes_response = [
        CartaoResponse.from_model(cartao, _token=criar_token_acesso(cartao.cpf_titular))
        for cartao in cartoes
    ]

    return CartoesPorCpfWrapper(
        status_code=status.HTTP_200_OK,
        message="Todos os cartões foram listados com sucesso.",
        data=CartoesPorCpfResponse(cartoes=cartoes_response),
    )


@router.put("/atualizar_info/{uuid}",
            response_model=CartaoUpdateWrapper,
            status_code=status.HTTP_200_OK,
            summary="Atualizar dados do cartão",
            description="Atualiza os dados do cartão pertencente ao UUID informado.",
            responses={
                **Responses.PutAtualizarInformacoes.sucesso_response,
                **Responses.PutAtualizarInformacoes.uuid_inexistente_response,
                **Responses.PutAtualizarInformacoes.dados_em_branco_response,
                **Responses.PutAtualizarInformacoes.erro_validacao_response
            })
async def atualizar_informacoes(dados_atualizados: CartaoUpdate,
                                uuid: UUID = Path(title="UUID do cartão.",
                                                 description="UUID do cartão a ser atualizado."),
                                db: AsyncSession = Depends(get_session),
                                _: str = Depends(get_current_user_cpf)) -> CartaoUpdateWrapper:

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

    if dados_atualizados.saldo is not None:
        atualizacoes_cartao["saldo"] = dados_atualizados.saldo
        cartao.saldo = dados_atualizados.saldo

    if not atualizacoes_cartao:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Erro. Não foram informados dados a serem atualizados.")

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Erro ao atualizar o cartão. Tente novamente mais tarde.")

    return CartaoUpdateWrapper(status_code=status.HTTP_200_OK,
                               message="Dados atualizados com sucesso.",
                               data=CartaoUpdateResponse.from_model(cartao))


@router.post("/transferir_saldo",
             response_model=CartaoTransferirWrapper,
             status_code=status.HTTP_200_OK,
             description="Transfere saldo entre cartões por UUID.")
async def transferir_saldo(transferencia: CartaoTransferir,
                           cartao_services: CartaoServices = Depends()) -> CartaoTransferirWrapper:

    cartao_response = await cartao_services.transferir_saldo(transferencia)

    return CartaoTransferirWrapper(
            status_code=cartao_response["status_code"],
            message=cartao_response["message"],
            data=cartao_response["data"]
        )
