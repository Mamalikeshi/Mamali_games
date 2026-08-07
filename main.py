from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from backend.database import init_database
from api import router
app = FastAPI(title="Mamali Games")
app.include_router(router)
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup():

    await init_database()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Mamali Games"
        }
    )


@app.get("/health")
async def health():

    return {
        "status": "ok",
        "version": "0.1"
    }
