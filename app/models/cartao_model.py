import enum, random
import uuid
from calendar import monthrange
from sqlalchemy import Enum, Column, Integer, String, Date, select, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timedelta, date
from jose import jwt
from app.database.base import Base, get_session
from app.core.configs import settings


class StatusEnum(enum.Enum):
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    CANCELADO = "CANCELADO"
    BLOQUEADO = "BLOQUEADO"
    ENVIADO = "ENVIADO"
    EXPIRADO = "EXPIRADO"
    EM_ANALISE = "EM_ANALISE"
    BLACKLISTED = "BLACKLISTED"


class CartaoModel(Base):
    __tablename__ = 'cartoes'

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    titular_cartao = Column(String, index=True, nullable=False)
    cpf_titular = Column(String, index=True, nullable=False)
    status = Column(Enum(StatusEnum), nullable=False, default=StatusEnum.EM_ANALISE)
    endereco = Column(String, index=True, nullable=False)
    numero_cartao = Column(String, nullable=False, unique=True)
    expiracao = Column(Date, nullable=False)
    cvv = Column(String, nullable=False)
    data_criacao = Column(DateTime(timezone=True), nullable=False)

    def __init__(self, titular_cartao, cpf_titular, endereco):
        super().__init__()
        self.titular_cartao = titular_cartao
        self.cpf_titular = cpf_titular
        self.endereco = endereco

    async def initialize(self):
        self.numero_cartao = await self.set_hash_cartao()
        self.cvv = self.set_hash_cvv()
        self.expiracao = self.gerar_data_expiracao()
        self.data_criacao = self.gerar_data_criacao()

    async def set_hash_cartao(self) -> str:
        numero_cartao = await self.gerar_numero_cartao()
        return self.gerar_hash_cartao(numero_cartao)

    @staticmethod
    async def gerar_numero_cartao() -> str:
        while True:
            numero_cartao = ''.join([str(random.randint(0, 9)) for _ in range(16)])
            if CartaoModel.validar_cartao(numero_cartao):
                if not await CartaoModel.verificar_hash_cartao_unico(numero_cartao):
                    return numero_cartao

    @staticmethod
    def validar_cartao(numero_cartao: str) -> bool:
        soma = 0
        invertido = numero_cartao[::-1]

        for i, digito in enumerate(invertido):
            n = int(digito)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            soma += n

        return soma % 10 == 0

    @staticmethod
    async def verificar_hash_cartao_unico(numero_cartao: str) -> bool:
        numero_cartao = CartaoModel.gerar_hash_cartao(numero_cartao)
        exists = False
        async for session in get_session():
            result = await session.execute(
                select(CartaoModel).filter_by(numero_cartao=numero_cartao)
            )
            if result is not None:
                exists = result.scalars().first()
        return exists is not None

    @staticmethod
    def gerar_hash_cartao(numero_cartao: str) -> str:
        payload = {"numero_cartao": numero_cartao}
        token = jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm=settings.ALGORITHM
        )
        return token

    def set_hash_cvv(self) -> str:
        cvv = self.gerar_cvv()
        return self.gerar_hash_cvv(cvv)

    @staticmethod
    def gerar_cvv() -> str:
        return ''.join([str(random.randint(0, 9)) for _ in range(3)])

    @staticmethod
    def gerar_hash_cvv(cvv: str) -> str:
        payload = {"cvv": cvv}
        token = jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm=settings.ALGORITHM
        )
        return token

    @staticmethod
    def gerar_data_expiracao() -> date:
        data_expiracao = datetime.now() + timedelta(days=5 * 365)
        ultimo_dia_do_mes = monthrange(data_expiracao.year, data_expiracao.month)[1]
        return datetime(data_expiracao.year, data_expiracao.month, ultimo_dia_do_mes).date()

    @staticmethod
    def gerar_data_criacao() -> datetime:
        return datetime.now()

    @staticmethod
    def descriptografar_hash_cartao(numero_cartao: str) -> str:
        payload = jwt.decode(
            numero_cartao,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM]
        )
        return payload.get('numero_cartao')

    @staticmethod
    def descriptografar_hash_cvv(hash_cvv: str) -> str:
        payload = jwt.decode(
            hash_cvv,
            settings.JWT_SECRET,
            algorithms=[settings.ALGORITHM]
        )
        return payload.get('cvv')

    @property
    def numero_cartao_descriptografado(self) -> str:
        return self.descriptografar_hash_cartao(self.numero_cartao)

    @property
    def cvv_descriptografado(self) -> str:
        return self.descriptografar_hash_cvv(self.cvv)
