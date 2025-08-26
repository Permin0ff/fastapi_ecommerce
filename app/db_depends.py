from sqlalchemy.orm import Session
from app.database import SessionLocal


async def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --------------- Асинхронная сессия -------------------------

from typing import AsyncGenerator
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Предоставляет асинхронную сессию SQLAlchemy для работы с базой данных PostgreSQL.
    """
    async with async_session_maker() as session:
        yield session
