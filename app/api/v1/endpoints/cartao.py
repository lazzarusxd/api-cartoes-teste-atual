from uuid import UUID
from fastapi import APIRouter, status, Depends
from app.api.v1.endpoints.responses.cartao_responses import Responses
from app.core.deps import auth_listar_cartoes_por_cpf, auth_atualizar_dados_cartao_uuid
from app.services.cartao_services import CartaoServices
from app.schemas.cartao_schema import (CriarCartao, CartaoResponseWrapper, CartoesPorCpfWrapper, CartaoUpdate,
                                       CartaoUpdateWrapper, CartaoTransferir, CartaoTransferirWrapper)

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
async def get_cartoes_por_cpf(cpf_titular: str = Depends(auth_listar_cartoes_por_cpf),
                              cartao_services: CartaoServices = Depends()) -> CartoesPorCpfWrapper:

    cartao_response = await cartao_services.listar_cartoes_por_cpf(cpf_titular)

    return CartoesPorCpfWrapper(
        status_code=cartao_response["status_code"],
        message=cartao_response["message"],
        data=cartao_response["data"]
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
                                uuid: UUID = Depends(auth_atualizar_dados_cartao_uuid),
                                cartao_services: CartaoServices = Depends()) -> CartaoUpdateWrapper:

    cartao_response = await cartao_services.atualizar_info(dados_atualizados, uuid)

    return CartaoUpdateWrapper(status_code=cartao_response["status_code"],
                               message=cartao_response["message"],
                               data=cartao_response["data"])


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
