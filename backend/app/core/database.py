import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

load_dotenv()

# =============================
# DATABASE CONFIGURATION (Única BD para toda la aplicación)
# =============================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5434/proyecto_ti"
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


def get_db() -> Session:
    """Dependency para inyectar sesión de BD en endpoints"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


