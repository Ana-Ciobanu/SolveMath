from fastapi import FastAPI
from controllers.controllers import router
from db.database import engine
from models.models import Base
from prometheus_fastapi_instrumentator import Instrumentator

def setup_monitoring(app):
    Instrumentator().instrument(app).expose(app)

app = FastAPI(title="Math Operations API", version="1.0")
app.include_router(router)

setup_monitoring(app)

# Create tables
Base.metadata.create_all(bind=engine)
