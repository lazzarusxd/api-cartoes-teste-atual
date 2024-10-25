from typing import Optional
from pytz import timezone
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt
from app.models.cartao_model import CartaoModel
from app.core.configs import settings
from pydantic import constr


oauth2_schema = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1}/login"
)


async def autenticar(cpf: constr(min_length=11, max_length=11), db: AsyncSession) -> Optional[CartaoModel]:
    query = select(CartaoModel).filter_by(cpf_titular=cpf)
    result = await db.execute(query)
    cartao = result.scalars().unique().one_or_none()

    if not cartao:
        return None

    return cartao


def _criar_token(tipo_token: str, tempo_vida: timedelta, sub: str) -> str:
    sp = timezone('America/Sao_Paulo')
    expira = datetime.now(tz=sp) + tempo_vida
    payload = {
        "type": tipo_token,
        "exp": expira,
        "iat": datetime.now(tz=sp),
        "sub": str(sub)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)


def criar_token_acesso(cpf: str) -> str:
    return _criar_token(
        tipo_token='access_token',
        tempo_vida=timedelta(minutes=settings.TOKEN_EXPIRATION_MINUTES),
        sub=cpf
    )
