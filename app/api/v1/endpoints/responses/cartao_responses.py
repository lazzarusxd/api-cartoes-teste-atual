class Responses:

    class PostSolicitarCartao:
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
                "description": "Erro de validação. Os parâmetros não atendem aos requisitos esperados.",
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

    class GetListarCartoes:
        sucesso_response = {
            200: {
                "description": "Todos os cartões foram listados com sucesso.",
                "content": {
                    "application/json": {
                        "example": {
                            "status_code": 200,
                            "message": "Todos os cartões foram listados com sucesso.",
                            "data": {
                                "cartoes": [
                                    {
                                        "uuid": "9534299a-8c90-473d-b9c6-cc2bb18103ae",
                                        "titular_cartao": "JOAO DA SILVA",
                                        "cpf_titular": "12345678912",
                                        "status": "EM_ANALISE",
                                        "endereco": "RUA DA FELICIDADE, BAIRRO ALEGRIA",
                                        "numero_cartao": "1111222233334444",
                                        "cvv": "123",
                                        "expiracao": "10/2029",
                                        "data_criacao": "16/10/2024 11:25:09"
                                    },
                                    {
                                        "uuid": "fb1d729b-46f7-4b2d-8b29-73eedc149e24",
                                        "titular_cartao": "MARIA DA SILVA",
                                        "cpf_titular": "21987654321",
                                        "status": "EM_ANALISE",
                                        "endereco": "RUA DA TRISTEZA, BAIRRO TRISTE",
                                        "numero_cartao": "4444333322221111",
                                        "cvv": "321",
                                        "expiracao": "10/2029",
                                        "data_criacao": "16/10/2024 11:24:47"
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }

    class GetListarCartoesCpf:
        sucesso_response = {
            200: {
                "description": "Todos os cartões foram listados com sucesso.",
                "content": {
                    "application/json": {
                        "example": {
                            "status_code": 200,
                            "message": "Todos os cartões foram listados com sucesso.",
                            "data": {
                                "cartoes": [
                                    {
                                        "uuid": "9534299a-8c90-473d-b9c6-cc2bb18103ae",
                                        "titular_cartao": "JOAO DA SILVA",
                                        "cpf_titular": "12345678912",
                                        "status": "EM_ANALISE",
                                        "endereco": "RUA DA FELICIDADE, BAIRRO ALEGRIA",
                                        "numero_cartao": "1111222233334444",
                                        "cvv": "123",
                                        "expiracao": "10/2029",
                                        "data_criacao": "16/10/2024 11:25:09"
                                    },
                                    {
                                        "uuid": "fb1d729b-46f7-4b2d-8b29-73eedc149e24",
                                        "titular_cartao": "JOAO DA SILVA",
                                        "cpf_titular": "12345678912",
                                        "status": "EM_ANALISE",
                                        "endereco": "RUA DA FELICIDADE, BAIRRO ALEGRIA",
                                        "numero_cartao": "4444333322221111",
                                        "cvv": "321",
                                        "expiracao": "10/2029",
                                        "data_criacao": "16/10/2024 11:24:47"
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }

        cpf_invalido_response = {
            404: {
                "description": "Erro no path. O CPF informado não foi encontrado.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "O CPF informado não foi encontrado."
                        }
                    }
                }
            }
        }

        erro_validacao_response = {
            422: {
                "description": "Erro de validação. Os parâmetros não atendem aos requisitos esperados.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": {
                                "loc": ["path", "cpf_titular"],
                                "msg": "CPF inválido. Forneça um CPF válido, composto por 11 números.",
                                "type": "value_error"
                            }
                        }
                    }
                }
            }
        }

    class PutAtualizarInformacoes:

        sucesso_response = {
            200: {
                "description": "Dados atualizados com sucesso.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": {
                                "status_code": 200,
                                "message": "Dados atualizados com sucesso.",
                                "data": {
                                    "uuid": "fb1d729b-46f7-4b2d-8b29-73eedc149e24",
                                    "titular_cartao": "JOAO DA SILVA",
                                    "cpf_titular": "12345678912",
                                    "status": "EM_ANALISE",
                                    "endereco": "RUA DA FELICIDADE, BAIRRO ALEGRIA",
                                    "numero_cartao": "4444333322221111",
                                    "cvv": "321",
                                    "expiracao": "10/2029",
                                    "data_criacao": "16/10/2024 11:24:47"
                                }
                            }
                        }
                    }
                }
            }
        }

        uuid_inexistente_response = {
            404: {
                "description": "Erro no path. O UUID informado não foi encontrado.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Cartão não encontrado, verifique o UUID."
                        }
                    }
                }
            }
        }

        erro_validacao_response = {
            422: {
                "description": "Erro de validação. Os parâmetros não atendem aos requisitos esperados.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": [
                                {
                                    "type": "uuid_parsing",
                                    "loc": ["path", "uuid"],
                                    "msg": "O UUID fornecido é inválido. O comprimento do primeiro grupo está incorreto: esperado 8, encontrado 7.",
                                    "input": "1045755-f41a-46f1-bc64-3da462dfec7a",
                                    "ctx": {
                                        "error": "invalid group length in group 0: expected 8, found 7"
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }

        dados_em_branco_response = {
            400: {
                "description": "Erro no body. Não foi informado nenhum dado para atualização.",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Erro no body. Não foi informado nenhum dado para atualizar."
                        }
                    }
                }
            }
        }

