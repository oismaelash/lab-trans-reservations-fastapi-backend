from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/reservas"
)

# Create engine with optimized settings
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Checks connections before using
    echo=False  # Set to True for SQL query debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for SQLAlchemy 2.x models
Base = declarative_base()


def get_db():
    """
    Dependency to get database session.
    Used as dependency injection in FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()