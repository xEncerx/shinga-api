from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.pool import AsyncAdaptedQueuePool

from src.core import settings

engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    connect_args={"server_settings": {"timezone": "UTC"}},
    pool_size=20,
    max_overflow=50,
    pool_pre_ping=False,
    pool_recycle=3600,
    poolclass=AsyncAdaptedQueuePool,
    future=True,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
