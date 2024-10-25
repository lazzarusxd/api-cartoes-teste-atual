from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from sqlalchemy.future import select
from pydantic import BaseModel, constr
from app.core.auth import oauth2_schema
from app.core.configs import settings
from app.database.base import get_session
from app.models.cartao_model import CartaoModel


class TokenData(BaseModel):
    cpf_titular: Optional[constr(min_length=11, max_length=11)] = None


async def get_current_user(db: AsyncSession = Depends(get_session),
                           token: str = Depends(oauth2_schema)) -> CartaoModel:

    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível autenticar a credencial.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False}
        )

        cpf_titular: str = payload.get("sub")

        if cpf_titular is None:
            raise credential_exception

        token_data = TokenData(cpf_titular=cpf_titular)

    except JWTError:
        raise credential_exception

    query = select(CartaoModel).filter_by(cpf_titular=token_data.cpf_titular)
    result = await db.execute(query)
    cartao: CartaoModel = result.scalars().unique().one_or_none()

    if cartao is None:
        raise credential_exception

    return cartao
