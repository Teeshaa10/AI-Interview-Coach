import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class MongoDB:
    """
    Owns the single MongoDB client for the process's lifetime.

    We wrap the raw motor client in a small class instead of calling
    AsyncIOMotorClient() wherever a database is needed, because:
    1. Motor's client already manages an internal connection pool —
       creating multiple clients means multiple pools, which wastes
       connections and can exhaust MongoDB Atlas's connection limit under
       load.
    2. One object with explicit connect()/close() methods gives us a clear
       hook for the FastAPI startup/shutdown lifecycle (see main.py).
    """

    client: AsyncIOMotorClient | None = None
    database: AsyncIOMotorDatabase | None = None


mongodb = MongoDB()


async def connect_to_mongo() -> None:
    """
    Opens the MongoDB connection. Called once, at application startup.

    AsyncIOMotorClient(...) is non-blocking — constructing it doesn't
    actually open a socket yet. We issue a `ping` command immediately after
    to force a real round-trip. This turns a silent, deferred connection
    failure into a loud, immediate one: if the URI or credentials are
    wrong, we find out at startup, not on a user's first request.
    """
    settings = get_settings()
    mongodb.client = AsyncIOMotorClient(settings.MONGODB_URI)
    mongodb.database = mongodb.client[settings.MONGODB_DB_NAME]

    await mongodb.client.admin.command("ping")
    logger.info(f"Connected to MongoDB database '{settings.MONGODB_DB_NAME}'")


async def close_mongo_connection() -> None:
    """Closes the MongoDB client cleanly. Called once, at application
    shutdown, so sockets aren't left open when the process exits."""
    if mongodb.client is not None:
        mongodb.client.close()
        logger.info("MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """
    FastAPI dependency that hands a route or service the active database
    handle. Routes call this via Depends(get_database) rather than
    importing `mongodb` directly — that indirection is what lets us swap in
    a fake database during tests without touching route code.
    """
    if mongodb.database is None:
        raise RuntimeError("MongoDB is not connected. Was connect_to_mongo() called?")
    return mongodb.database
