from passlib.context import CryptContext

CRIPTO = CryptContext(schemes=['bcrypt'], deprecated='auto')

def verificar_hash(valor: str, hash_valor: str) -> bool:
    return CRIPTO.verify(valor, hash_valor)

def gerar_hash(valor: str) -> str:
    return CRIPTO.hash(valor)
