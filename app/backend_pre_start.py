import logging
import asyncio

from app.db.init_db import init_db

from db.session import SessionLocal
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init() -> None:
    try:
        db = SessionLocal()
        await init_db(db)
        # Try to create session to check if DB is awake
        # db.execute("SELECT 1")
    except Exception as e:
        logger.error(e)
        raise e
    finally:
        await db.close()


async def main() -> None:
    logger.info("Initializing service")
    await init()
    logger.info("Service finished initializing")


if __name__ == "__main__":
   asyncio.run(main())
