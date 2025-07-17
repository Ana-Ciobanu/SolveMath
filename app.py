from fastapi import FastAPI
from controllers.controllers import router
from db.database import engine
from models.models import Base

app = FastAPI(title="Math Operations API", version="1.0")
app.include_router(router)

# Create tables
Base.metadata.create_all(bind=engine)
