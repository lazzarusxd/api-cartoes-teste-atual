import pytest
from typing import AsyncGenerator
from httpx import AsyncClient
from fastapi import status
from uuid import uuid4
from app.main import app
from app.models.cartao_model import CartaoModel
from app.database.base import get_session
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
async def setup_db() -> AsyncGenerator[AsyncSession, None]:
    # Cria uma nova sessão
    async with get_session() as session:
        async with session.begin():  # Inicia uma transação
            yield session  # Permite que o teste use a sessão
            await session.rollback()


# Teste para o endpoint de solicitar cartão (POST /solicitar_cartao)
@pytest.mark.asyncio
async def test_solicitar_cartao(setup_db: AsyncSession):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        request_data = {
            "titular_cartao": "João Silva",
            "cpf_titular": "12345678901",
            "endereco": "Rua Exemplo, 123"
        }
        response = await ac.post("/api/v1/cartoes/solicitar_cartao", json=request_data)

        print(response.status_code)  # Debugging
        print(response.json())       # Debugging

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["message"] == "Cartão criado com sucesso."
    assert response.json()["data"]["titular_cartao"] == "JOÃO SILVA"


# Teste para erro ao tentar criar cartão com CPF já existente para titular diferente
@pytest.mark.asyncio
async def test_solicitar_cartao_cpf_existente(setup_db: AsyncSession):
    # Pré-cadastrando um cartão para simular a duplicidade de CPF
    cartao_existente = CartaoModel(titular_cartao="Maria Oliveira", cpf_titular="12345678901", endereco="Rua 1")
    setup_db.add(cartao_existente)
    await setup_db.commit()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        request_data = {
            "titular_cartao": "João Silva",
            "cpf_titular": "12345678901",
            "endereco": "Rua Exemplo, 123"
        }
        response = await ac.post("/api/v1/cartoes/solicitar_cartao", json=request_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "CPF já cadastrado para um titular diferente."


# Teste para listar todos os cartões (GET /listar_cartoes/todos)
@pytest.mark.asyncio
async def test_listar_todos_cartoes(setup_db: AsyncSession):
    # Pré-cadastrando alguns cartões
    cartao1 = CartaoModel(titular_cartao="João Silva", cpf_titular="12345678901", endereco="Rua 1")
    cartao2 = CartaoModel(titular_cartao="Maria Oliveira", cpf_titular="98765432100", endereco="Rua 2")
    setup_db.add_all([cartao1, cartao2])
    await setup_db.commit()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/cartoes/listar_cartoes/todos")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["data"]["cartoes"]) == 2


# Teste para listar cartões por CPF (GET /listar_cartoes/cpf/{cpf_titular})
@pytest.mark.asyncio
async def test_listar_cartoes_por_cpf(setup_db: AsyncSession):
    cartao1 = CartaoModel(titular_cartao="João Silva", cpf_titular="12345678901", endereco="Rua 1")
    setup_db.add(cartao1)
    await setup_db.commit()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/cartoes/listar_cartoes/cpf/12345678901")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["cartoes"][0]["cpf_titular"] == "12345678901"


# Teste para cartão não encontrado pelo CPF
@pytest.mark.asyncio
async def test_listar_cartao_por_cpf_nao_encontrado(setup_db: AsyncSession):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/cartoes/listar_cartoes/cpf/00000000000")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Cartão não encontrado, verifique o UUID."


# Teste para atualizar informações do cartão (PUT /atualizar_info/{uuid})
@pytest.mark.asyncio
async def test_atualizar_informacoes_cartao(setup_db: AsyncSession):
    cartao = CartaoModel(titular_cartao="João Silva", cpf_titular="12345678901", endereco="Rua 1")
    setup_db.add(cartao)
    await setup_db.commit()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        update_data = {
            "titular_cartao": "João Pedro Silva",
            "endereco": "Rua Nova, 456"
        }
        response = await ac.put(f"/api/v1/cartoes/atualizar_info/{cartao.uuid}", json=update_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["titular_cartao"] == "João Pedro Silva"
    assert response.json()["data"]["endereco"] == "Rua Nova, 456"


# Teste para erro ao tentar atualizar cartão com UUID inexistente
@pytest.mark.asyncio
async def test_atualizar_informacoes_cartao_nao_encontrado(setup_db: AsyncSession):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        update_data = {
            "titular_cartao": "João Pedro Silva",
            "endereco": "Rua Nova, 456"
        }
        response = await ac.put(f"/api/v1/cartoes/atualizar_info/{uuid4()}", json=update_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Cartão não encontrado, verifique o UUID."


# Teste para erro ao tentar atualizar sem dados
@pytest.mark.asyncio
async def test_atualizar_informacoes_sem_dados(setup_db: AsyncSession):
    cartao = CartaoModel(titular_cartao="João Silva", cpf_titular="12345678901", endereco="Rua 1")
    setup_db.add(cartao)
    await setup_db.commit()

    async with AsyncClient(app=app, base_url="http://test") as ac:
        update_data = {}
        response = await ac.put(f"/api/v1/cartoes/atualizar_info/{cartao.uuid}", json=update_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Erro. Não foi informado nenhum dado para atualizar."
