class Response:
    sucesso_response = {
        201: {
            "description": "Cartão criado com sucesso.",
            "content": {
                "application/json": {
                    "example": {
                        "status_code": 201,
                        "message": "Cartão criado com sucesso.",
                        "data": {
                            "titular_cartao": "JOSE DA SILVA",
                            "cpf_titular": "23948273849",
                            "endereco": "RUA II, S/N, BAIRRO TRINTA",
                            "status": "EM_ANALISE"
                        }
                    }
                }
            }
        }
    }

    erro_validacao_response = {
        422: {
            "description": "Erro de validação. Ocorre quando os parâmetros não atendem aos requisitos esperados.",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "nome_titular"],
                                "msg": "Nome inválido. Forneça um nome válido, constituído apenas por letras.",
                                "type": "value_error"
                            },
                            {
                                "loc": ["body", "cpf_titular"],
                                "msg": "CPF inválido. Forneça um CPF válido, composto por 11 números.",
                                "type": "value_error"
                            },
                            {
                                "loc": ["body", "endereco"],
                                "msg": "Endereço inválido. O campo endereço não pode ficar vazio.",
                                "type": "value_error"
                            }
                        ]
                    }
                }
            }
        }
    }
