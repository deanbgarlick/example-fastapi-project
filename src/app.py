from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.db_models import Base
from src.db import engine
from src.routers import items
from src.logging import configure_logging, with_default_logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Configure logging at application startup
    configure_logging()
    # Create database tables
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
@with_default_logging
async def healthcheck():
    return {"status": "healthy", "message": "API is running"}

# Include the items router
app.include_router(items.router)