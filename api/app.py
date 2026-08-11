from fastapi import FastAPI

from .routes import router


app = FastAPI(
    title="Mamali Games API",
    version="0.1",
)

app.include_router(router)
