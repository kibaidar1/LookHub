from asyncio import current_task
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable, AsyncContextManager

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
)
from sqlalchemy.orm import sessionmaker

from app.config import DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME

# Construct database URL from configuration
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create async engine with default settings
engine = create_async_engine(DATABASE_URL)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@asynccontextmanager
async def scoped_session() -> Callable[[], AsyncContextManager[AsyncSession]]:
    """Create a scoped session factory for the current task.
    
    This function creates a session factory that is scoped to the current asyncio task,
    ensuring that each task gets its own session. The session is automatically
    cleaned up when the task completes.
    
    Returns:
        Callable: A factory function that creates async context managers for sessions
        
    Yields:
        AsyncSession: The scoped database session
        
    Note:
        The session is automatically removed when the task completes or if an error occurs
    """
    scoped_factory = async_scoped_session(
        async_session_maker,
        scopefunc=current_task,
    )
    try:
        async with scoped_factory() as session:
            yield session
    finally:
        await scoped_factory.remove()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session.
    
    This function provides a session factory that can be used as a FastAPI dependency
    for database access. The session is automatically closed when the request completes.
    
    Yields:
        AsyncSession: An async database session
        
    Note:
        This function is designed to be used as a FastAPI dependency
    """
    async with async_session_maker() as session:
        yield session
