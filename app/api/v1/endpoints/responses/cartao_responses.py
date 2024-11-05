class Responses:

    class SolicitarCartao:
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
                                "status": "EM_ANALISE",
                                "token": "eyJhbGckpXVCJ9.eyJ0eXBlDM3MDA00.tVmBVYdL3iKNgR4yn6t7xj9"
                            }
                        }
                    }
                }
            }
        }

        dados_em_branco = {
            400: {
                "description": "Possíveis erros de validação (regras de negócio e campos vazios).",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": [
                                "O nome do titular deve ser composto apenas por letras.",
                                "Nome titular é um campo obrigatório e não pode ser uma string vazia.",
                                "Endereço é um campo obrigatório e não pode ser uma string vazia.",
                                "CPF é um campo obrigatório e não pode ser uma string vazia.",
                                "O CPF deve conter apenas números.",
                                "O CPF deve conter exatamente 11 dígitos.",
                                "CPF já cadastrado para um titular diferente."
                            ]
                        }
                    }
                }
            }
        }

    class CartoesPorCpf:
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
                                        "saldo": 50.0,
                                        "numero_cartao": "1111222233334444",
                                        "cvv": "123",
                                        "expiracao": "10/2029",
                                        "data_criacao": "16/10/2024 11:25:09",
                                        "token": "eyJhbGckpXVCJ9.eyJ0eXBlDM3MDA00.tVmBVYdL3iKNgR4yn6t7xj9"
                                    },
                                    {
                                        "uuid": "fb1d729b-46f7-4b2d-8b29-73eedc149e24",
                                        "titular_cartao": "JOAO DA SILVA",
                                        "cpf_titular": "12345678912",
                                        "status": "EM_ANALISE",
                                        "endereco": "RUA DA FELICIDADE, BAIRRO ALEGRIA",
                                        "saldo": 150.0,
                                        "numero_cartao": "4444333322221111",
                                        "cvv": "321",
                                        "expiracao": "10/2029",
                                        "data_criacao": "16/10/2024 11:24:47",
                                        "token": "eyJhbGckpXVCJ9.eyJ0eXBlDM3MDA00.tVmBVYdL3iKNgR4yn6t7xj9"
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

    class AtualizarDados:

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
                                    "status": "ATIVO",
                                    "endereco": "RUA DA FELICIDADE, BAIRRO ALEGRIA",
                                    "saldo": 50.0,
                                    "numero_cartao": "4444333322221111",
                                    "cvv": "321",
                                    "expiracao": "10/2029",
                                    "data_criacao": "16/10/2024 11:24:47",
                                    "token": "eyJhbGckpXVCJ9.eyJ0eXBlDM3MDA00.tVmBVYdL3iKNgR4yn6t7xj9"
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

        dados_em_branco_response = {
            400: {
                "description": "Possíveis erros de validação (regras de negócio e campos vazios/nulos).",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": [
                                "Erro. Não foram informados dados a serem atualizados.",
                                "O nome do titular não pode ser uma string vazia.",
                                "O nome do titular deve ser composto apenas por letras.",
                                "Endereço inválido. O endereço não pode ser vazio.",
                                "CPF é um campo obrigatório e não pode ser vazio."
                            ]
                        }
                    }
                }
            }
        }

    class RecarregarCartao:
        ...

    class TransferirSaldo:
        ...
