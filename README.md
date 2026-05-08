# Proyecto TI - Sistema Integrado

## Descripción
Sistema integrado de gestión con módulos principales:
1. **Módulo de Subscripciones** (Legacy)
2. **Módulo de Salud** (Nuevo - Arquitectura Data Warehouse)

Todos los módulos comparten **1 sola BD PostgreSQL** con tablas organizadas por lógica.

---

## 🏗️ Arquitectura

### Base de Datos (Única)
- **PostgreSQL 16**: puerto 5434
- **Base de datos**: `proyecto_ti`
- Docker Compose gestiona 1 contenedor
- **Tablas separadas** para cada módulo/lógica

### Módulo de Salud - Data Warehouse
```
┌─────────────────────────────┐
│  API REST (20+ Endpoints)   │
├─────────────────────────────┤
│  Services (Lógica)          │
├─────────────────────────────┤
│  Raw Layer (Eventos)        │  ← Captura
│  - 13 tablas                │
├─────────────────────────────┤
│  Warehouse Layer (Análisis) │  ← Análisis
│  - 4 tablas (Dim + Fact)    │
├─────────────────────────────┤
│  PostgreSQL (Puerto 5434)   │
│  Base de datos única        │
└─────────────────────────────┘
```

---

## 🚀 Quick Start (5 minutos)

### 1. Levantar Base de Datos
```bash
docker-compose up -d
```

### 2. Configurar Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno
```bash
copy .env.example .env
# El archivo ya tiene valores por defecto (1 sola BD)
```

### 4. Ejecutar Backend
```bash
python -m fastapi dev
```

Backend disponible en: `http://localhost:8000`

### 5. Generar Datos de Prueba (Opcional)
```bash
curl -X POST http://localhost:8000/seed/salud
```

---

## 📊 Endpoints del Módulo de Salud

**Ver documentación completa**: [ENDPOINTS_BY_MODULE.md](ENDPOINTS_BY_MODULE.md)

### Dashboard
- `GET /api/v1/salud/dashboard` - Resumen del módulo

### Pacientes (6 endpoints)
- `POST /api/v1/salud/pacientes/` - Crear
- `GET /api/v1/salud/pacientes/` - Listar
- `GET /api/v1/salud/pacientes/{id}` - Obtener
- `PUT /api/v1/salud/pacientes/{id}` - Actualizar
- `DELETE /api/v1/salud/pacientes/{id}` - Eliminar
- `GET /api/v1/salud/pacientes/{id}/estadisticas` - Estadísticas

### Visitas (7 endpoints)
- `POST /api/v1/salud/visitas/` - Crear
- `GET /api/v1/salud/visitas/` - Listar
- `GET /api/v1/salud/visitas/{id}` - Obtener
- `PUT /api/v1/salud/visitas/{id}` - Actualizar
- `POST /api/v1/salud/visitas/{id}/completar` - Completar
- `POST /api/v1/salud/visitas/{id}/cancelar` - Cancelar
- `GET /api/v1/salud/visitas/hoy/programadas` - Hoy

### Alertas (6 endpoints)
- `POST /api/v1/salud/alertas/` - Crear
- `GET /api/v1/salud/alertas/` - Listar
- `GET /api/v1/salud/alertas/{id}` - Obtener
- `PUT /api/v1/salud/alertas/{id}` - Actualizar
- `POST /api/v1/salud/alertas/{id}/resolver` - Resolver
- `GET /api/v1/salud/alertas/resumen/por-prioridad` - Resumen

**Total: 20+ endpoints completamente funcionales**

---

## 📁 Estructura de Datos (Una sola BD)

### Raw Layer (Captura de Eventos)
Tablas con prefijo `raw_`:
```sql
raw_usuarios, raw_pacientes, raw_visitas, raw_alertas
raw_fichas_clinicas, raw_documentos_adjuntos
```

### Warehouse Layer (Análisis)
Tablas con prefijo `dim_` y `fact_`:
```sql
dim_pacientes, dim_profesionales
fact_visitas, fact_alertas
```

### Subscripciones (Legacy)
Tablas del módulo original:
```sql
subscripciones, usuarios_subscripciones, etc.
```

---

## 🎨 Paleta de Colores

```
#353535 - Graphite (Crítico)
#3C6E71 - Stormy Teal (Exitoso)
#284B63 - Yale Blue (Alerta)
#D9D9D9 - Alabaster Grey (Neutro)
#FFFFFF - White
```

---

## 📚 Documentación

| Archivo | Descripción |
|---------|-------------|
| [ENDPOINTS_BY_MODULE.md](ENDPOINTS_BY_MODULE.md) | Endpoints organizados por módulo ⭐ |
| [SETUP.md](SETUP.md) | Guía completa de instalación |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Referencia rápida de comandos |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Detalles técnicos |
| [backend/sql/schemas.sql](backend/sql/schemas.sql) | Esquemas SQL |

---

## 📖 Acceder a Documentación Interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI**: http://localhost:8000/openapi.json

---

## 🔧 Variables de Entorno (.env)

```env
# Base de Datos (Única para toda la aplicación)
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5434/proyecto_ti
DEBUG=True
SQL_ECHO=False
ENVIRONMENT=development
```

---

## 🧪 Validar Setup

```bash
python scripts/validate_setup.py
```

Verifica:
- ✅ Imports correctos
- ✅ Conectividad BD
- ✅ Tablas registradas
- ✅ Docker containers

---

## 🛠️ Solución de Problemas

### Error: Connection refused (5434)
```bash
# Verificar Docker
docker ps

# Revisar logs
docker logs proyecto_ti_postgres
```

### Error: database does not exist
```bash
docker-compose down -v
docker-compose up -d
```

### Ejecutar esquemas SQL manualmente
```bash
# Conectar a BD
psql -U postgres -h localhost -p 5434 -d proyecto_ti

# Copiar contenido de: backend/sql/schemas.sql
```

---

## 📋 Estructura de Carpetas

```
backend/
├── app/
│   ├── core/
│   │   └── database.py          ← Config BD única
│   ├── db/                      ← Subscripciones legacy
│   ├── models/                  ← Subscripciones legacy
│   ├── modules/
│   │   └── health/
│   │       ├── models/          ← Raw (6) + Warehouse (4)
│   │       ├── routes/          ← Endpoints API
│   │       ├── services/        ← Lógica
│   │       ├── schemas/         ← Pydantic
│   │       ├── scripts/         ← Seed data
│   │       └── router.py        ← Router consolidado
│   └── __init__.py
├── sql/
│   └── schemas.sql              ← Todos esquemas
├── scripts/
│   └── validate_setup.py        ← Validación
├── main.py                      ← App principal
├── requirements.txt
├── .env.example
└── docker-compose.yml
```

---

## ✨ Características Implementadas

✅ **Una sola Base de Datos** - Simplificación
✅ **Arquitectura Modular** - Estructura organizada por responsabilidad
✅ **Data Warehouse** - Raw + Warehouse layers
✅ **API REST** - 20+ endpoints documentados
✅ **Tablas Separadas** - Lógica diferenciada por prefijo
✅ **Seed Data** - 33 registros de prueba
✅ **Documentación** - Completa y actualizada
✅ **Color Palette** - Integrada en schemas
✅ **Docker** - 1 contenedor simplificado

---

## 🔄 Flujo de Datos

```
1. Usuario crea Paciente
   ↓
2. POST /api/v1/salud/pacientes/
   ↓
3. Service inserta en raw_pacientes
   ↓
4. [ETL Job] Transforma a dim_pacientes
   ↓
5. Dashboard accede a warehouse para análisis
```

---

## 🎯 Próximos Pasos

1. **Frontend** - Componentes Next.js con paleta de colores
2. **Power BI** - Conectar warehouse para dashboards
3. **ETL** - Jobs automáticos Raw → Warehouse
4. **Auth** - JWT para seguridad
5. **WebSockets** - Alertas en tiempo real

---

## 📞 Comandos Útiles

```bash
# Docker
docker-compose up -d       # Levantar
docker-compose ps          # Estado
docker-compose down        # Detener

# Backend
python -m fastapi dev      # Desarrollo
pip install -r requirements.txt  # Deps

# Testing
curl -X POST http://localhost:8000/seed/salud
curl http://localhost:8000/api/v1/salud/dashboard
```

---

**¡Sistema completamente funcional y documentado! 🚀**

Última actualización: Mayo 7, 2026


---

## 🚀 Quick Start (5 minutos)

### 1. Levantar Bases de Datos
```bash
docker-compose up -d
```

### 2. Configurar Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno
```bash
copy .env.example .env
# El archivo ya tiene valores por defecto
```

### 4. Ejecutar Backend
```bash
python -m fastapi dev
```

Backend disponible en: `http://localhost:8000`

### 5. Generar Datos de Prueba (Opcional)
```bash
curl -X POST http://localhost:8000/seed/salud
```

---

## 📊 Endpoints del Módulo de Salud

**Ver documentación completa**: [ENDPOINTS_BY_MODULE.md](ENDPOINTS_BY_MODULE.md)

### Dashboard
- `GET /api/v1/salud/dashboard` - Resumen del módulo

### Pacientes (6 endpoints)
- `POST /api/v1/salud/pacientes/` - Crear
- `GET /api/v1/salud/pacientes/` - Listar
- `GET /api/v1/salud/pacientes/{id}` - Obtener
- `PUT /api/v1/salud/pacientes/{id}` - Actualizar
- `DELETE /api/v1/salud/pacientes/{id}` - Eliminar
- `GET /api/v1/salud/pacientes/{id}/estadisticas` - Estadísticas

### Visitas (7 endpoints)
- `POST /api/v1/salud/visitas/` - Crear
- `GET /api/v1/salud/visitas/` - Listar
- `GET /api/v1/salud/visitas/{id}` - Obtener
- `PUT /api/v1/salud/visitas/{id}` - Actualizar
- `POST /api/v1/salud/visitas/{id}/completar` - Completar
- `POST /api/v1/salud/visitas/{id}/cancelar` - Cancelar
- `GET /api/v1/salud/visitas/hoy/programadas` - Hoy

### Alertas (6 endpoints)
- `POST /api/v1/salud/alertas/` - Crear
- `GET /api/v1/salud/alertas/` - Listar
- `GET /api/v1/salud/alertas/{id}` - Obtener
- `PUT /api/v1/salud/alertas/{id}` - Actualizar
- `POST /api/v1/salud/alertas/{id}/resolver` - Resolver
- `GET /api/v1/salud/alertas/resumen/por-prioridad` - Resumen

**Total: 20+ endpoints completamente funcionales**

---

## 📁 Estructura de Datos

### Raw Layer (Captura de Eventos)
```sql
roles, zonas, usuarios, auditorias
profesionales_salud, especialidades
profesional_zona, profesional_especialidad
pacientes, visitas, alertas
fichas_clinicas, documentos_adjuntos
```

### Warehouse Layer (Análisis)
```sql
dim_pacientes       → Dimensión pacientes
dim_profesionales   → Dimensión profesionales
fact_visitas        → Hechos visitas
fact_alertas        → Hechos alertas
```

---

## 🎨 Paleta de Colores

```
#353535 - Graphite (Crítico)
#3C6E71 - Stormy Teal (Exitoso)
#284B63 - Yale Blue (Alerta)
#D9D9D9 - Alabaster Grey (Neutro)
#FFFFFF - White
```

---

## 📚 Documentación

| Archivo | Descripción |
|---------|-------------|
| [ENDPOINTS_BY_MODULE.md](ENDPOINTS_BY_MODULE.md) | Endpoints organizados por módulo ⭐ |
| [SETUP.md](SETUP.md) | Guía completa de instalación |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Referencia rápida de comandos |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Detalles técnicos |
| [backend/sql/schemas.sql](backend/sql/schemas.sql) | Esquemas SQL |

---

## 📖 Acceder a Documentación Interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI**: http://localhost:8000/openapi.json

---

## 🔧 Variables de Entorno (.env)

```env
# BD Subscripciones (Legacy)
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5434/proyecto_ti
DEBUG=True

# BD Salud (Data Warehouse)
SALUD_DATABASE_URL=postgresql://postgres:postgres@localhost:5435/proyecto_ti_salud

# Configuración General
SQL_ECHO=False
ENVIRONMENT=development
```

---

## 🧪 Validar Setup

```bash
python scripts/validate_setup.py
```

Verifica:
- ✅ Imports correctos
- ✅ Conectividad BD
- ✅ Tablas registradas
- ✅ Docker containers

---

## 🛠️ Solución de Problemas

### Error: Connection refused (5435)
```bash
# Verificar Docker
docker ps

# Revisar logs
docker logs proyecto_ti_postgres_salud
```

### Error: database does not exist
```bash
docker-compose down
docker-compose up -d
```

### Ejecutar esquemas SQL manualmente
```bash
# Conectar a BD Salud
psql -U postgres -h localhost -p 5435 -d proyecto_ti_salud

# Copiar contenido de: backend/sql/schemas.sql
```

---

## 📋 Estructura de Carpetas

```
backend/
├── app/
│   ├── core/
│   │   └── database.py          ← Config multi-BD
│   ├── db/                      ← Subscripciones legacy
│   ├── models/                  ← Subscripciones legacy
│   ├── modules/
│   │   └── health/
│   │       ├── models/          ← Raw (6) + Warehouse (4)
│   │       ├── routes/          ← Endpoints API
│   │       ├── services/        ← Lógica
│   │       ├── schemas/         ← Pydantic
│   │       ├── scripts/         ← Seed data
│   │       └── router.py        ← Router consolidado
│   └── __init__.py
├── sql/
│   └── schemas.sql              ← Todos esquemas
├── scripts/
│   └── validate_setup.py        ← Validación
├── main.py                      ← App principal
├── requirements.txt
├── .env.example
└── docker-compose.yml
```

---

## ✨ Características Implementadas

✅ **Arquitectura Modular** - Estructura organizada por responsabilidad
✅ **Data Warehouse** - Raw + Warehouse layers
✅ **API REST** - 20+ endpoints documentados
✅ **BD Separadas** - Scalabilidad horizontal
✅ **Seed Data** - 33 registros de prueba
✅ **Documentación** - Completa y actualizada
✅ **Color Palette** - Integrada en schemas
✅ **Docker** - Multi-contenedor

---

## 🔄 Flujo de Datos

```
1. Usuario crea Paciente
   ↓
2. POST /api/v1/salud/pacientes/
   ↓
3. Service inserta en raw_pacientes
   ↓
4. [ETL Job] Transforma a dim_pacientes
   ↓
5. Dashboard accede a warehouse para análisis
```

---

## 🎯 Próximos Pasos

1. **Frontend** - Componentes Next.js con paleta de colores
2. **Power BI** - Conectar warehouse para dashboards
3. **ETL** - Jobs automáticos Raw → Warehouse
4. **Auth** - JWT para seguridad
5. **WebSockets** - Alertas en tiempo real

---

## 📞 Comandos Útiles

```bash
# Docker
docker-compose up -d       # Levantar
docker-compose ps          # Estado
docker-compose down        # Detener

# Backend
python -m fastapi dev      # Desarrollo
pip install -r requirements.txt  # Deps

# Testing
curl -X POST http://localhost:8000/seed/salud
curl http://localhost:8000/api/v1/salud/dashboard
```

---

**¡Sistema completamente funcional y documentado! 🚀**

Última actualización: Mayo 7, 2026

