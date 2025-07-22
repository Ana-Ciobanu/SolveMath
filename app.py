from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from controllers.controllers import router
from db.database import engine
from models.models import Base
from prometheus_fastapi_instrumentator import Instrumentator
import logging
from utils.logging_db import DBLogHandler
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi import Depends, HTTPException
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from controllers.controllers import verify_token
from fastapi.responses import Response

db_handler = DBLogHandler()
db_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(db_handler)


def setup_monitoring(app):
    Instrumentator().instrument(app)


app = FastAPI(title="Math Operations API", version="1.0")
app.include_router(router)


app.mount("/view", StaticFiles(directory="view"), name="view")


@app.get("/")
def read_root():
    return FileResponse("view/frontend.html")


@app.get("/admin/metrics", tags=["Admin"])
def admin_metrics(token: dict = Depends(verify_token)):
    if token.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend())


setup_monitoring(app)


# Create tables
Base.metadata.create_all(bind=engine)
