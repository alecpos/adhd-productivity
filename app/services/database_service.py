from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker


class DatabaseService:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self._session: Optional[AsyncSession] = None
        self._engine = create_async_engine(db_url)
        self._async_session = sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )

    async def get_session(self) -> AsyncSession:
        if not self._session:
            self._session = self._async_session()
        return self._session
