from uuid import UUID
from fastapi import Depends, HTTPException, status, Path
from jose import jwt, JWTError
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.auth import oauth2_schema
from app.models.cartao_model import CartaoModel
from app.core.configs import settings
from app.database.base import get_session


async def auth_listar_cartoes_por_cpf(cpf_titular: str = Path(title="CPF do titular",
                                                              description="CPF do titular do cartão."),
                                      token: str = Depends(oauth2_schema),
                                      db: AsyncSession = Depends(get_session)) -> str:

    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credencial inválida para o CPF vinculado.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM],
        )
        token_cpf = payload.get("sub")

        if not token_cpf or token_cpf != cpf_titular:
            raise credential_exception

        query = select(CartaoModel).where(CartaoModel.cpf_titular == token_cpf)
        result = await db.execute(query)
        cartao = result.scalars().first()

        if not cartao or cartao.hash_token_descriptografado != token:
            raise credential_exception

        return token_cpf

    except JWTError:
        raise credential_exception


async def auth_atualizar_dados_cartao_uuid(uuid: UUID = Path(title="UUID do cartão",
                                                             description="UUID do cartão do titular."),
                                           token: str = Depends(oauth2_schema),
                                           db: AsyncSession = Depends(get_session)) -> UUID:  # Alterado para retornar UUID

    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credencial inválida para o CPF vinculado ao cartão.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        token_cpf = payload.get("sub")

        if not token_cpf:
            raise credential_exception

        # A consulta correta deve ser feita com UUID
        query = select(CartaoModel).where(
            and_(
                CartaoModel.uuid == uuid)
        )
        result = await db.execute(query)
        cartao = result.scalars().first()

        if not cartao:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Não foi encontrado cartão com o UUID informado.")

        # Verificação correta do CPF
        if cartao.cpf_titular != token_cpf or cartao.hash_token_descriptografado != token:
            raise credential_exception

        return cartao.uuid  # Retorne o UUID do cartão

    except JWTError:
        raise credential_exception
