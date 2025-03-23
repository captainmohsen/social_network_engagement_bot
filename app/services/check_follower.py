import aiohttp
from sqlalchemy.future import select
from app.db.session import SessionLocal as AsyncSessionLocal
from app.models import Track, FollowerHistory
from app.services.telegram_message import TelegramNotifier
from app.services.mock_data import get_mock_follower_count
from datetime import datetime, timedelta
from app import crud
import logging
from app import crud,schemas


USE_MOCK_DATA = True
logging.basicConfig(level=logging.INFO)

class FollowerChecker:
    def __init__(self):
        self.telegram = TelegramNotifier()
        self.db = AsyncSessionLocal()


    async def fetch_follower_count(self, social_media, profile_username):
        if USE_MOCK_DATA:
            return get_mock_follower_count(social_media, profile_username)

        API_URLS = {
            "Instagram": f"https://api.instagram.com/v1/users/{profile_username}/followers",
            "Twitter": f"https://api.twitter.com/2/users/by/username/{profile_username}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(API_URLS.get(social_media)) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("followers_count", 0)
                return None

    async def check_followers(self):
        logging.info("🔄 Running inside follower check task...****************")

        result = await self.db.execute(select(Track).where(Track.alert_enabled == True))
        tracks = result.scalars().all()
        logging.info(tracks)

        for track in tracks:
            logging.info(track.profile_username)

            new_follower_count = await self.fetch_follower_count(track.social_media, track.profile_username)
            if new_follower_count is not None and new_follower_count != track.last_follower_count:
                logging.info("inside check tracks........")
                follower_history_in = schemas.FollowerHistoryCreate(
                    track_id=track.id,
                    follower_count=new_follower_count
                )
                follower_history = await crud.follower_history.create(db=self.db, obj_in=follower_history_in)
                await self.db.commit()

                track.last_follower_count = new_follower_count
                await self.db.add(track)
                await self.db.commit()
                await self.db.refresh(track)

                if new_follower_count >= track.alert_threshold:
                    await self.telegram.send_alert(track.profile_username, track.alert_threshold)

        await self.db.commit()

    async def get_top_changes(self, hours=24, top_n=5):
        time_threshold = datetime.utcnow() - timedelta(hours=hours)

        async with self.db as session:
            async with session.begin():
                result = await session.execute(
                    select(FollowerHistory.track_id, FollowerHistory.follower_count)
                    .where(FollowerHistory.created_at >= time_threshold)
                    .order_by(FollowerHistory.created_at.desc())
                )
                rows = result.fetchall()

        changes = {}
        for track_id, count in rows:
            if track_id in changes:
                changes[track_id]["end"] = count
            else:
                changes[track_id] = {"start": count, "end": count}

        result_changes = [
            {"track_id": track_id, "change": data["end"] - data["start"]}
            for track_id, data in changes.items()
        ]

        result_changes.sort(key=lambda x: abs(x["change"]), reverse=True)

        return result_changes[:top_n]

    async def get_engagement(self, profile_username: str):
        async with AsyncSessionLocal() as session:
            async with session.begin():
                track = await crud.track.get_by_profile_username(db=self.db, profile_username=profile_username)

                if not track:
                    return None

                time_threshold = datetime.utcnow() - timedelta(hours=24)
                history_result = await session.execute(
                    select(FollowerHistory.follower_count)
                    .where(FollowerHistory.track_id == track.id, FollowerHistory.created_at >= time_threshold)
                    .order_by(FollowerHistory.created_at.asc())
                )

                history = history_result.scalars().all()
                if not history:
                    return 0.0

                first_count = history[0]
                last_count = track.last_follower_count

                follower_change = abs(last_count - first_count)
                engagement_rate = (follower_change / last_count) * 100 if last_count > 0 else 0

                return round(engagement_rate, 2)



