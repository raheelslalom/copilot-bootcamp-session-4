"""Database configuration and session management"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Get database URL from environment or use SQLite as default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./capabilities.db"
)

# Create engine with appropriate options
if DATABASE_URL.startswith("sqlite"):
    # SQLite specific options
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    # PostgreSQL or other databases
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for models
Base = declarative_base()


def get_db():
    """Dependency for injecting database session into FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)
