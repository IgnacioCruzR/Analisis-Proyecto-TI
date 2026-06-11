import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Load .env.local from project root
# __file__ is at: ...backend/app/db/session.py
# We need to go up 3 levels to reach the project root
current_dir = Path(__file__).resolve()
project_root = current_dir.parent.parent.parent.parent  # Up 4 levels to project root
env_file = project_root / ".env.local"

if env_file.exists():
    load_dotenv(env_file)
else:
    # Fallback to .env or environment variables
    load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        f"DATABASE_URL environment variable is not set. "
        f"Expected .env.local at {env_file} or DATABASE_URL in environment."
    )


engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "False").lower() == "true",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Session:  # ty:ignore[invalid-return-type]
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()
