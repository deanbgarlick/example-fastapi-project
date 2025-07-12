from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Callable, Iterator, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
import os
from enum import Enum, auto

class DBType(Enum):
    SQLITE = auto()
    NEON = auto()

def get_db_url(db_type: DBType) -> str:
    if db_type == DBType.SQLITE:
        return "sqlite:///example.db"
    elif db_type == DBType.NEON:
        # Get the Neon database URL from environment variable
        neon_url = os.getenv("DATABASE_URL")
        if not neon_url:
            raise ValueError("DATABASE_URL environment variable not set for Neon database")
        return neon_url
    raise ValueError(f"Unsupported database type: {db_type}")

def get_db_builder(db_type: DBType) -> Tuple[Callable[[], Iterator[Session]], Engine]:
    """
    Creates a database session factory and engine based on the specified database type.
    
    Args:
        db_type: The type of database to connect to (SQLite or Neon)
        
    Returns:
        A tuple containing (session_factory, engine)
    """
    database_url = get_db_url(db_type)
    
    # Configure SQLAlchemy engine with appropriate settings for each database type
    if db_type == DBType.SQLITE:
        engine = create_engine(database_url, connect_args={"check_same_thread": False})
    else:  # Neon (PostgreSQL)
        engine = create_engine(database_url)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    def get_db() -> Iterator[Session]:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    return get_db, engine

# Create specific database factories
def get_sqlite_db():
    return get_db_builder(DBType.SQLITE)

def get_neon_db():
    return get_db_builder(DBType.NEON)

# Configure database - default to SQLite for local development
DB_TYPE = DBType.SQLITE
get_db, engine = get_db_builder(DB_TYPE)
