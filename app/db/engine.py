from sqlalchemy.ext.asyncio import create_async_engine

from app.core import settings

engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    connect_args={"server_settings": {"timezone": "UTC"}},
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
)