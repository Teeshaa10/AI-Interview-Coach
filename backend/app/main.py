from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.resume import router as resume_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.chroma import connect_to_chroma
from app.db.mongo import close_mongo_connection, connect_to_mongo
from app.exceptions.handlers import register_exception_handlers
from app.repositories.user_repository import UserRepository
from app.repositories.resume_repository import ResumeRepository


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """
#     Defines what happens on startup and shutdown.

#     This is FastAPI's current mechanism for lifecycle hooks, replacing the
#     older @app.on_event("startup") / @app.on_event("shutdown") decorators.
#     Everything before `yield` runs exactly once, when the server starts;
#     everything after `yield` runs exactly once, when the server shuts down.
#     We use it to open the Mongo and Chroma connections a single time (not
#     per-request — that would be catastrophic for performance) and to close
#     Mongo cleanly on shutdown rather than leaving sockets open when the
#     process exits.
#     """
#     setup_logging()
#     await connect_to_mongo()
#     connect_to_chroma()

#     # Ensures the unique email index exists before the app accepts traffic.
#     # create_index is idempotent — safe to call on every startup, not just
#     # the first — so this needs no separate migration step for Module 1.
#     # from app.db.mongo import mongodb

#     # await UserRepository(mongodb.database).create_indexes()

#     # yield
#     # await close_mongo_connection()
#     from app.db.mongo import mongodb

# await UserRepository(mongodb.database).create_indexes()
# await ResumeRepository(mongodb.database).ensure_indexes()

# yield
# await close_mongo_connection()
@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await connect_to_mongo()
    connect_to_chroma()

    from app.db.mongo import mongodb

    await UserRepository(mongodb.database).create_indexes()
    await ResumeRepository(mongodb.database).ensure_indexes()

    yield

    await close_mongo_connection()


settings = get_settings()

app = FastAPI(
    title="AI Interview Coach API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

# /health stays unversioned and un-prefixed: load balancers and uptime
# monitors expect a stable, predictable path that never changes across API
# versions. Feature routes live under /api/v1 so a future v2 can be
# introduced without breaking v1 clients.
app.include_router(health_router)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(resume_router, prefix="/api/v1")
