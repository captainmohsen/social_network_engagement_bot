import aiohttp
import logging
from app.core.config import settings
from app.db.session import SessionLocal as AsyncSessionLocal
from app import crud

logging.basicConfig(level=logging.INFO)

class TelegramNotifier:
    def __init__(self):
        self.TOKEN = settings.TELEGRAM_TOKEN
        self.API_URL = settings.TELEGRAM_API_URL
        self.db = AsyncSessionLocal()


    async def get_chat_id(self, username: str):
        """Fetch user's chat_id from database"""
        user = await crud.user.get_by_username(db=self.db,username=username)
        return user.chat_id if user else None

    async def send_alert(self, username, threshold):
        message = f"🎉 {username} to  {threshold} has been reached"
        data = {"chat_id": self.get_chat_id(username=username), "text": message}

        async with aiohttp.ClientSession() as session:
            async with session.post(self.API_URL, data=data) as response:
                if response.status == 200:
                    logging.info(f"✅ message for {username} sent")
                else:
                    logging.error(f"❌ error in sending message  {response.status}, {await response.text()}")
