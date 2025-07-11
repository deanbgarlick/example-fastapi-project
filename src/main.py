from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.db_models import Base
from src.database import engine
from src.routers import items

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def healthcheck():
    return {"status": "healthy", "message": "API is running"}

# Include the items router
app.include_router(items.router)