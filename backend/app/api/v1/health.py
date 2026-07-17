from chromadb import ClientAPI
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import get_chroma_client, get_database

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(
    db: AsyncIOMotorDatabase = Depends(get_database),
    chroma: ClientAPI = Depends(get_chroma_client),
) -> dict:
    """
    Reports whether the API and each of its dependencies are reachable.

    This is deliberately more than a "the server is on" check — it pings
    Mongo and Chroma independently, because "the FastAPI process is
    running" and "the FastAPI process can actually serve a real request"
    are different facts. A load balancer or uptime monitor hitting this
    endpoint should be able to tell, from the response body alone, which
    dependency is down if something breaks — that's the entire reason to
    build this now rather than bolting it on after the first outage.
    """
    mongo_status = "ok"
    try:
        await db.command("ping")
    except Exception:
        mongo_status = "unreachable"

    chroma_status = "ok"
    try:
        chroma.heartbeat()
    except Exception:
        chroma_status = "unreachable"

    overall = "ok" if mongo_status == "ok" and chroma_status == "ok" else "degraded"

    return {
        "status": overall,
        "dependencies": {
            "mongodb": mongo_status,
            "chromadb": chroma_status,
        },
    }
