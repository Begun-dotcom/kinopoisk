from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config import setting
from app.core.base import Base  # Импортируем из core
from app.dao.dao import BannerDao
from app.utils.utils import banner_text

URL = setting.STORE_URL
async_engine = create_async_engine(url=URL)
async_session_maker = async_sessionmaker(bind=async_engine, class_=AsyncSession)

async def create_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session_maker() as session:
        await BannerDao(session=session).add_banner(data=banner_text)

async def drop_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)