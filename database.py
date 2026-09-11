import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


# Allows changing the database without modifying the source code.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/api_docker",
)

# Manages communication between SQLAlchemy and PostgreSQL.
engine = create_engine(DATABASE_URL)

# Creates a separate database session for each API request.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    # User and Project models will inherit from this class.
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        # FastAPI uses this session during the current request.
        yield db
    finally:
        # Closes the session even if the request raises an error.
        db.close()