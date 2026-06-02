# Análisis Proyecto TI

## Servicios necesarios

| Servicio   | Origen                                                                 | Puerto |
| ---------- | ---------------------------------------------------------------------- | ------ |
| Postgres   | `docker-compose.yml` (este repo)                                       | 5434   |
| Backend    | FastAPI (`backend/`)                                                   | 8000   |
| Frontend   | Next.js (`Frontend/`)                                                  | 3000   |
| Keycloak   | Repo del equipo de identidad: `git@gitlab.com:bloppaa/sistema-identidad.git` | 8080   |

## 0) Levantar Keycloak (otro repo)

En una carpeta **fuera** de este proyecto:

```bash
git clone git@gitlab.com:bloppaa/sistema-identidad.git
cd sistema-identidad
docker compose up -d
```

Consola admin: <http://localhost:8080> (admin / admin).

Pedir al equipo de identidad que registre nuestro cliente en el realm
`sistema-centralizado` con:

| Campo                 | Valor                          |
| --------------------- | ------------------------------ |
| Client ID             | `proyecto-analisis-ti`         |
| Client authentication | **Off** (cliente público)      |
| Standard flow         | ✓                              |
| Direct access grants  | ✓                              |
| Valid redirect URIs   | `http://localhost:3000/*`      |
| Web origins           | `http://localhost:3000`        |

Si cambia el Client ID, hay que actualizar:

- `Frontend/.env` → `NEXT_PUBLIC_KEYCLOAK_CLIENT_ID`
- (no afecta al backend, que solo valida tokens del realm)

## 1) Levantar Postgres

```bash
docker compose up -d
```

## 2) Levantar backend (FastAPI)

Primera vez:

```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m fastapi dev
```

Si ya tienes `.venv`:

```bash
cd backend
.venv\Scripts\Activate.ps1
python -m fastapi dev
```

Endpoints útiles para probar la integración con Keycloak:

- `GET /auth/status` — público, dice si el token es válido.
- `GET /auth/me` — exige `Authorization: Bearer <jwt>`, devuelve el usuario.

## 3) Levantar frontend (Next.js)

```bash
cd Frontend
npm install
npm run dev
```

Al abrir <http://localhost:3000> el frontend redirige automáticamente al login
de Keycloak. Tras autenticarse vuelve al dashboard con el token cargado, y
todas las llamadas a la API ya viajan con `Authorization: Bearer <jwt>`.

## Roles y permisos

El sistema usa **roles de realm** de Keycloak (`sistema-centralizado`).
Mantener en sync con `backend/app/api/routes/kpis.py` (constantes
`SUBS_ROLES`, `ORDERS_ROLES`, etc.) y `Frontend/lib/roles.ts`
(`ROLE_MATRIX`).

### Roles definidos

| Rol             | Descripción                                                |
| --------------- | ---------------------------------------------------------- |
| `admin`         | Acceso total. Ve todos los dashboards.                     |
| `analista`      | Lectura de todos los dashboards (overview + 4 dominios).   |
| `salud`         | Equipo de salud. Solo `/kpis/salud/*` y `/health`.         |
| `subscriptions` | Equipo de suscripciones. Solo `/kpis/subscriptions/*`.     |
| `orders`        | Equipo de órdenes. Solo `/kpis/orders/*` y `/orders`.      |
| `incidents`     | Equipo de incidentes. Solo `/kpis/incidents/*`.            |

### Matriz de acceso (backend)

| Endpoint                | Roles permitidos                          |
| ----------------------- | ----------------------------------------- |
| `/auth/*`, `/events/*`  | cualquier autenticado                     |
| `/kpis/overview/*`      | `admin`, `analista`                       |
| `/kpis/orders/*`        | `admin`, `analista`, `orders`             |
| `/kpis/subscriptions/*` | `admin`, `analista`, `subscriptions`      |
| `/kpis/salud/*`         | `admin`, `analista`, `salud`              |
| `/kpis/incidents/*`     | `admin`, `analista`, `incidents`          |

Sin token o con rol incorrecto, el backend responde `401` o `403`.
El frontend filtra el sidebar y bloquea las páginas con `<RoleGate>`.

### Bootstrap del realm (importante)

El container Keycloak del equipo de identidad arranca con
`start-dev --import-realm` y **sin volumen persistente**: cada reinicio
del container deja el realm con su configuración inicial y se pierden
los roles/usuarios/clients hechos por consola admin.

Para recuperar el estado funcional en cualquier momento, basta correr
el script idempotente que está en este repo:

```powershell
.\scripts\bootstrap-keycloak.ps1
```

Crea/actualiza:

- Los **6 roles** (`admin`, `analista`, `salud`, `subscriptions`, `orders`, `incidents`).
- Los **6 usuarios de prueba** con sus contraseñas y roles asignados.
- El **client público** `proyecto-analisis-ti` con `redirectUris=http://localhost:3000/*` y `webOrigins=http://localhost:3000`.

Si el container del equipo de identidad cambia de URL/puerto, pasarlo:

```powershell
.\scripts\bootstrap-keycloak.ps1 -KeycloakUrl http://otra-url:8080
```

### Usuarios de prueba (entorno local)

Estos usuarios los crea/actualiza el script de bootstrap. **Solo para
desarrollo local** — no usar en producción.

| Usuario        | Email                  | Password       | Roles asignados |
| -------------- | ---------------------- | -------------- | --------------- |
| `admingrupo9`  | admin@ucn.cl           | `admin`        | `admin`         |
| `analista`     | analista@ucn.cl        | `Analista123!` | `analista`      |
| `salud`        | salud@ucn.cl           | `Salud123!`    | `salud`         |
| `subscriptions`| subscriptions@ucn.cl   | `Subs123!`     | `subscriptions` |
| `orders`       | orders@ucn.cl          | `Orders123!`   | `orders`        |
| `incidents`    | incidents@ucn.cl       | `Inc123!`      | `incidents`     |

Al hacer login en <http://localhost:3000>, cada usuario ve solo los menús
y dashboards que le corresponden.

## Cómo proteger un endpoint del backend

```python
from fastapi import Depends
from app.auth import get_current_user, require_roles, require_any_role, KeycloakUser

@router.get("/protegido")
def protegido(user: KeycloakUser = Depends(get_current_user)):
    return {"hola": user.username}

# Exige TODOS los roles listados.
@router.get("/solo-admin", dependencies=[Depends(require_roles("admin"))])
def solo_admin():
    return {"ok": True}

# Exige al menos UNO de los roles (lo que usan los endpoints de KPIs).
@router.get("/kpis-salud", dependencies=[Depends(require_any_role(["admin", "analista", "salud"]))])
def kpis_salud():
    return {"ok": True}
```

Los endpoints de `/kpis/*` ya exigen los roles de la matriz de arriba.
Los de `/events/*` siguen abiertos a cualquier autenticado (el frontend
manda el token, pero no se discrimina por rol al ingestar eventos).

## Variables de entorno

`Frontend/.env`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_KEYCLOAK_URL=http://localhost:8080
NEXT_PUBLIC_KEYCLOAK_REALM=sistema-centralizado
NEXT_PUBLIC_KEYCLOAK_CLIENT_ID=proyecto-analisis-ti
```

`backend/.env`:

```
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5434/proyecto_ti
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=sistema-centralizado
KEYCLOAK_AUDIENCE=account
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```
