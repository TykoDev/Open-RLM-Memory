import asyncio

# Add backend directory to path to allow imports
import os
import sys

from loguru import logger
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all models to ensure they are registered
import app.models  # noqa
from app.core.config import settings
from app.database.connection import engine
from app.models.base import Base


async def init_db():
    logger.info(f"Initializing database: {settings.DB_TYPE} at {settings.DATABASE_URL}")

    try:
        async with engine.begin() as conn:
            if engine.url.get_backend_name().startswith("postgresql"):
                logger.info("Creating pgvector extension...")
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                try:
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_prewarm"))
                except Exception as exc:
                    logger.warning(f"pg_prewarm extension unavailable: {exc}")
                try:
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_buffercache"))
                except Exception as exc:
                    logger.warning(f"pg_buffercache extension unavailable: {exc}")

            logger.info("Creating tables...")
            await conn.run_sync(Base.metadata.create_all)

            # Verify
            def get_tables(connection):
                from sqlalchemy import inspect

                return inspect(connection).get_table_names()

            tables = await conn.run_sync(get_tables)
            logger.info(f"Tables created: {tables}")

            if "memory" in tables:
                logger.info("SUCCESS: 'memory' table exists.")
            else:
                logger.error("FAILURE: 'memory' table missing.")

    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(init_db())
