from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)

async_session = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session