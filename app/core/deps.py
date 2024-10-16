"""from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from sqlalchemy.future import select
from pydantic import BaseModel
from app.core.auth import oauth2_schema
from app.core.configs import settings
from usuario_model import UsuarioModel
from app.database.session import get_session


class TokenData(BaseModel):
    user_id: Optional[str] = None


async def get_current_user(
        db: AsyncSession = Depends(get_session),
        token: str = Depends(oauth2_schema)) -> UsuarioModel:
    credential_exception: HTTPException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível autenticar a credencial",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False}
        )
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credential_exception

        token_data = TokenData(user_id=user_id)

    except JWTError:
        raise credential_exception

    query = select(UsuarioModel).filter_by(id=int(token_data.user_id))
    result = await db.execute(query)
    usuario: UsuarioModel = result.scalars().unique().one_or_none()

    if usuario is None:
        raise credential_exception

    return usuario
"""