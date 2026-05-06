import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/proyecto_ti"
)

# Crear engine
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Mostrar las queries SQL
    pool_pre_ping=True,  # Verificar conexión antes de usar
)

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

# Dependencia para inyectar sesiones en FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
