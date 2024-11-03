from typing import Optional
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from pydantic import BaseModel, constr
from app.core.auth import oauth2_schema
from app.core.configs import settings


class TokenData(BaseModel):
    cpf_titular: Optional[constr(min_length=11, max_length=11)] = None


async def get_current_user_cpf(token: str = Depends(oauth2_schema)) -> str:

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
            options={"verify_aud": False}
        )
        cpf_titular = payload.get("sub")

        if cpf_titular is None:
            raise credential_exception

        return cpf_titular

    except JWTError:
        raise credential_exception
