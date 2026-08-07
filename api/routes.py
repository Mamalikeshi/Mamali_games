from fastapi import APIRouter

router = APIRouter()


@router.get("/api/status")
async def status():

    return {
        "project": "Mamali Games",
        "status": "online",
        "version": "0.1"
    }
