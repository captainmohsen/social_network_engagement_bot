
from app.core.config import settings
import asyncio
import logging
from app.services.check_follower import FollowerChecker

logging.basicConfig(level=logging.INFO)


async def run_follower_check():
    """
    Background task to check follower counts periodically.
    """
    checker = FollowerChecker()

    while True:
        try:
            logging.info("🔄 Running follower check task...")
            await checker.check_followers()
        except Exception as e:
            logging.error(f"❌ Error in background task: {e}")

        await asyncio.sleep(settings.FOLLOWER_CHECKER_INTERVAL)

