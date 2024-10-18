from fastapi import FastAPI
from app.core.configs import settings
from app.api.v1.api import router
from dotenv import load_dotenv


load_dotenv()
app = FastAPI(
    title="API de Gerenciamento de Cartões",
    description="""
    API responsável pelo gerenciamento de cartões de crédito, com recursos que incluem:

    - Solicitação de cartão: Gera um novo cartão válido (algoritmo de Luhn) para um titular existente.
    - Listar cartões: Recupera todos os cartões cadastrados no banco.
    - Listar cartões por CPF: Recupera todos os cartões cadastrados no banco, vinculados ao CPF inserido.
    - Atualizar cartões por UUID: Atualiza informações do titular (nome completo e endereço) e o status do cartão.

    # Autenticação e Segurança:
    
    A API não salva informações sensíveis como (número de cartão e cvv) diretamente no banco de dados. Em vez disso, são utilizados métodos de criptografia e hash para garantir a segurança dos dados sensíveis. O CPF e o nome do titular também são validados para garantir a integridade dos dados.

    # Endpoints disponíveis:
    
    - POST /solicitar_cartao: Solicita um novo cartão para um usuário.
    - GET /listar_cartoes/todos: Lista de todos os cartões.
    - GET /listar_cartoes/cpf/{cpf_titular}: Lista os cartões vinculados a um CPF específico.
    - PUT /atualizar_info/{uuid}: Atualização dos dados de um cartão existente.

    # Possíveis erros:
    
    - 400: Erros de validação ou ao processar solicitações.
    - 422: Erros em envio de parâmetros.
    - 404: Cartão não encontrado para o CPF ou UUID informado.
    - 500: Erro interno do servidor.
    """,
    version="1.1"
)

app.include_router(router, prefix=settings.API_V1)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level='debug', reload=True)
