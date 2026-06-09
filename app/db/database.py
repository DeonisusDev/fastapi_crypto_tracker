from dotenv import load_dotenv
from app.models.coin import Base
import os
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
assert DATABASE_URL, "DATABASE_URL is not set in .env"

engine = create_async_engine(DATABASE_URL)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    """
    Provides an asynchronous database session for use in API routes and other operations.
    This function is designed to be used as a dependency in FastAPI routes, ensuring that
    a new database session is created for each request and properly closed after use.
    
    Yields:
        An instance of AsyncSession for interacting with the database.
    
    Raises:
        Exception: If any error occurs while creating or yielding the database session.
    """
    async with SessionLocal() as session:
        yield session

async def create_tables():
    """
    Creates the database tables based on the SQLAlchemy models defined in the application.
    This function should be called during the application startup to ensure that the necessary
    tables are created before any operations are performed on the database.
    Raises:
        Exception: If any error occurs during the table creation process.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)