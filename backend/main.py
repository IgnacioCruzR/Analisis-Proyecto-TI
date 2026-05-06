from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.db import engine, Base, get_db
from app.models import RawEvent, FactSubscription  # noqa: F401 - Import models for SQLAlchemy registry

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
