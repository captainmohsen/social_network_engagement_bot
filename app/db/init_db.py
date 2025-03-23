import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.core.config import settings

logger = logging.getLogger(__name__)


async def init_db(db: AsyncSession) -> None:
    """Initialize the database with default  users"""
    test_user = await crud.user.get_by_username(db=db,username=settings.TEST_USER_USERNAME)
    if not test_user:
        user_in = schemas.UserCreate(
            password=settings.TEST_USER_PASSWORD,
            username=settings.TEST_USER_USERNAME,
            email=settings.TEST_USER_EMAIL,
        )
        user = await crud.user.create(db, obj_in=user_in)
        await db.commit()

        logger.info("✅ Test user created: test_user / test_password")

    await db.close()


logger.info("Database initialization complete!")


