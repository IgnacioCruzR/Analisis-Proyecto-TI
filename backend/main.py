from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from config.database import engine, Base, get_db

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
