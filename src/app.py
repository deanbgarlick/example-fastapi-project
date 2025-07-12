from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from src.models.db_models import Base
from src.db import engine
from src.routers import items
from src.logging import configure_logging, with_default_logging
from src.rate_limiter import rate_limiter, rate_limit_handler
from slowapi.errors import RateLimitExceeded

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Configure logging at application startup
    configure_logging()
    # Create database tables
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)
app.state.limiter = rate_limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

@app.get("/")
@rate_limiter.limit("10/second")
@with_default_logging
async def healthcheck(request: Request):
    return {"status": "healthy", "message": "API is running"}

# Include the items router
app.include_router(items.router)