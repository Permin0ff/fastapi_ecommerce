from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker


engine = create_async_engine('postgresql+asyncpg://ecommerce:251125@localhost:5432/ecommerce', echo=True)

#engine = create_async_engine('sqlite+aiosqlite:///myfile.db')

async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

