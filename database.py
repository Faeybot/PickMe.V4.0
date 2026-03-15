import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update
from models import Base, User
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL").replace("postgresql://", "postgresql+aiopg://")

engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    async with engine.begin() as conn:
        # Membuat tabel secara otomatis saat bot pertama kali jalan
        await conn.run_sync(Base.metadata.create_all)

async def reset_quotas():
    async with async_session() as session:
        async with session.begin():
            await session.execute(update(User).values(swipe_quota=30))
        await session.commit()
      
