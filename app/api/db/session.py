from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.api.db.models import Base


class SessionHandler:
    def __init__(self, cfg):
        db = cfg.db
        url = f'postgresql+asyncpg://{db.user}:{db.password}@localhost:{db.port}/{db.name}'
        print(url)
        self.engine = create_async_engine(
            url,
            echo=db.echo_log,
        )
        self.async_session = sessionmaker(self.engine,
                                          class_=AsyncSession,
                                          expire_on_commit=False)

    async def init_models(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

