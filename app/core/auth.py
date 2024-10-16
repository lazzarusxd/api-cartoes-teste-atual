"""from typing import Optional
from pytz import timezone
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt
from usuario_model import UsuarioModel
from app.core.configs import settings
from app.core.security import verificar_senha
from pydantic import EmailStr


oauth2_schema = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1}/cartoes"
)


async def autenticar(email: EmailStr, senha: str, db: AsyncSession) -> Optional[UsuarioModel]:
    query = select(UsuarioModel).filter_by(email=email)
    result = await db.execute(query)
    usuario = result.scalars().unique().one_or_none()

    if not usuario or not verificar_senha(senha, usuario.senha):
        return None

    return usuario


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


def criar_token_acesso(sub: str) -> str:
    # https://jwt.io (verifica a validade da assinatura)
    return _criar_token(
        tipo_token='access_token',
        tempo_vida=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        sub=sub
    )
"""