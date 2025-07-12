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
        # Get the Neon database URL from secrets/environment variables
        neon_url = os.getenv("DATABASE_URL")
        if neon_url:
            # If DATABASE_URL is set, use it directly
            return neon_url
        
        # Otherwise, construct URL from individual secrets
        host_file = os.getenv("NEON_HOST_FILE", "secrets/neon_host.txt")
        username_file = os.getenv("NEON_USERNAME_FILE", "secrets/neon_username.txt")
        password_file = os.getenv("NEON_PASSWORD_FILE", "secrets/neon_password.txt")
        
        if host_file and username_file and password_file:
            try:
                with open(host_file, 'r') as f:
                    host = f.read().strip()
                with open(username_file, 'r') as f:
                    username = f.read().strip()
                with open(password_file, 'r') as f:
                    password = f.read().strip()
                
                # Construct PostgreSQL URL
                # The host file already contains the full endpoint with database and SSL params
                neon_url = f"postgresql://{username}:{password}@{host}"
                return neon_url
            except FileNotFoundError as e:
                raise ValueError(f"Could not read Neon secrets file: {e}")
        
        raise ValueError("Either DATABASE_URL or all Neon secret files (NEON_HOST_FILE, NEON_USERNAME_FILE, NEON_PASSWORD_FILE) must be set")
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
DB_TYPE = DBType.NEON
get_db, engine = get_db_builder(DB_TYPE)
