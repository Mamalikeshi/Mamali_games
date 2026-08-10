from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.hokm import router as hokm_router
from api.chahar_barg import router as chahar_barg_router

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

app.include_router(hokm_router)
app.include_router(chahar_barg_router)


@app.get("/")
def home():
    return {
        "success": True,
        "message": "Mamali Games API is running",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
    }
