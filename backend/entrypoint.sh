#!/bin/sh
set -e

echo "Aplicando migraciones de base de datos..."
alembic upgrade head

echo "Iniciando servidor..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
