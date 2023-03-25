from typing import Optional, TYPE_CHECKING, Callable
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker


if TYPE_CHECKING:
    from kts_backend.web.app import Application

db = declarative_base()


class Database:
    def __init__(self, app: "Application"):
        self.app = app
        self._engine: Optional[AsyncEngine] = None
        self._db: Optional[declarative_base] = None
        self.session: Optional[Callable[[], AsyncSession]] = None

    async def connect(self, *_: list, **__: dict) -> None:
        self._db = db
        self._engine = create_async_engine(
            "postgresql+asyncpg://gameadmin:123@localhost:5432/svoyak",
            echo=True,
            future=True,
        )
        self.session = sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )

    async def disconnect(self, *_: list, **__: dict) -> None:
        if self.session:
            self.session = None
        if self._engine:
            await self._engine.dispose()
