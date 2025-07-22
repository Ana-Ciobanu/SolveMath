from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from controllers.controllers import router
from db.database import engine
from models.models import Base
from prometheus_fastapi_instrumentator import Instrumentator
import logging
from utils.logging_db import DBLogHandler

db_handler = DBLogHandler()
db_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(db_handler)

def setup_monitoring(app):
    Instrumentator().instrument(app).expose(app)

app = FastAPI(title="Math Operations API", version="1.0")
app.include_router(router)

app.mount("/view", StaticFiles(directory="view"), name="view")

@app.get("/")
def read_root():
    return FileResponse("view/frontend.html")


setup_monitoring(app)


# Create tables
Base.metadata.create_all(bind=engine)
