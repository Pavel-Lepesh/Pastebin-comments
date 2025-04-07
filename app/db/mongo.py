from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.comments.models import Comment
from app.config import settings
from loguru import logger


async def init_mongo():
    client = AsyncIOMotorClient(f"mongodb://{settings.MONGODB_HOST}:{settings.MONGODB_PORT}")
    database = client[f"{settings.MONGODB_DB_NAME}"]
    await init_beanie(
        database=database,
        document_models=[Comment,]
    )

    logger.info("MongoDB initialised")
