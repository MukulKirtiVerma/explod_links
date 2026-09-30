from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import STATIC_DIR
from app.routers import api, pages

app = FastAPI(title="Explode Links")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(pages.router)
app.include_router(api.router)
