from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.configs import settings
from typing import AsyncGenerator

engine: AsyncEngine = create_async_engine(settings.DB_URL, pool_pre_ping=True, future=True, echo=True)

Base = declarative_base()

LocalAsyncSession = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with LocalAsyncSession() as session:
        yield session
