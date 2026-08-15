from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes import router as api_router
from backend.database import init_database

app = FastAPI(
    title="Mamali Games",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.on_event("startup")
async def on_startup():
    await init_database()


@app.get("/health")
def health():
    return {"status": "ok"}


# این خط باید همیشه آخرین خط باشه: صفحات frontend/ رو روی آدرس اصلی سرو می‌کنه
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
