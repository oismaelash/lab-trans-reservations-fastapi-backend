[Ver vídeo de demonstração](https://github.com/oismaelash/lab-trans-reservations-fastapi-backend/raw/refs/heads/main/demo.mp4)

# Room Reservation System - Backend

RESTful API developed with **FastAPI**, **PostgreSQL** and **SQLAlchemy** for room reservation management with conflict validation, soft delete and location and room administration.

## 📖 English Summary

### Project Overview

This is a **RESTful API** for managing room reservations in a multi-location system. The API provides endpoints for managing locations, rooms, and reservations with comprehensive validation, conflict detection, and soft delete functionality. It's built with modern Python technologies and follows best practices for API development.

### Technology Stack

- **Python 3.12** - Main programming language
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy 2.x** - ORM for database operations
- **Alembic** - Database migration tool
- **Pydantic v2** - Data validation and serialization
- **PostgreSQL 16** - Relational database
- **Uvicorn** - ASGI server
- **Docker & Docker Compose** - Containerization
- **PDM** - Python dependency manager

### Business Rules

#### Soft Delete
- All entities (Locations, Rooms, Reservations) implement soft delete
- Deleted records are marked with `deleted_at` timestamp but remain in database
- Deleted records are excluded from queries and return 404 when accessed directly

#### Time Conflict Validation
- Two reservations conflict if their time ranges overlap in the same room
- Conflict formula: `new_start < existing_end AND new_end > existing_start`
- **Adjacent times are allowed** (e.g., 10:00-11:00 and 11:00-12:00 are valid)

#### Date and Timezone Rules
- All dates stored in **UTC** in the database
- API accepts dates in **ISO 8601** format (e.g., `2025-11-19T10:00:00Z`)
- **Reservations in the past are not allowed** (validated on create/update)

#### Coffee Service Rule
- If `cafe = true`, then `quantidade_cafe` is required and must be > 0
- If `cafe = false` or omitted, `quantidade_cafe` is ignored/zeroed

#### Additional Validations
- Room names must be unique within the same location
- Rooms must belong to an active location
- Reservations must reference active locations and rooms
- Start date must be strictly less than end date (not equal)

### Running the Project

#### Option 1: Local Development (Without Docker)

**Prerequisites:**
- Python 3.12 installed
- PostgreSQL 16 installed and running
- PDM installed (`pip install pdm`)

**Steps:**

1. **Install dependencies:**
   ```bash
   cd backend
   pdm install
   ```

2. **Set up PostgreSQL database:**
   ```bash
   # Create database
   createdb reservas
   
   # Or using psql
   psql -U postgres -c "CREATE DATABASE reservas;"
   ```

3. **Configure environment variables:**
   Create a `.env` file in the `backend/` folder:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/reservas
   CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
   ```

4. **Apply database migrations:**
   ```bash
   pdm run alembic upgrade head
   ```

5. **Run the API:**
   ```bash
   pdm run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Verify it's working:**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status": "healthy", "database": "connected"}
   ```

**Access the API:**
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

#### Option 2: Docker & Docker Compose (Recommended)

**Prerequisites:**
- Docker and Docker Compose installed

**Steps:**

1. **Configure environment variables:**
   Create a `.env` file in the `backend/` folder:
   ```env
   DATABASE_URL=postgresql://user:password@db:5432/reservas
   POSTGRES_USER=user
   POSTGRES_PASSWORD=password
   POSTGRES_DB=reservas
   CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
   ```

2. **Start containers:**
   ```bash
   cd backend
   docker compose up -d
   ```

3. **Apply database migrations:**
   ```bash
   docker compose exec api alembic upgrade head
   ```

4. **Verify health check:**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status": "healthy", "database": "connected"}
   ```

**Useful Docker commands:**
```bash
# View logs
docker compose logs -f api
docker compose logs -f db

# Stop services
docker compose down

# Stop and remove volumes (deletes data)
docker compose down -v

# Restart API
docker compose restart api

# Rebuild and restart
docker compose up -d --build api
```

**Access the API:**
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🛠️ Technology Stack

- **Python 3.12** - Main language
- **FastAPI** - Modern and fast web framework
- **SQLAlchemy 2.x** - ORM for PostgreSQL communication
- **Alembic** - Migration system for schema management
- **Pydantic v2** - Data validation and schemas
- **PostgreSQL 16** - Relational database
- **Uvicorn** - High performance ASGI server
- **Docker & Docker Compose** - Containerization and orchestration
- **PDM** - Modern Python package manager

## 🚀 How to Run the Project

### Prerequisites

- **Docker** and **Docker Compose** installed
- **Git** to clone the repository

### Step 1: Configure Environment Variables

Create a `.env` file in the `backend/` folder with the following variables:

```env
# PostgreSQL Configuration
DATABASE_URL=postgresql://user:password@db:5432/reservas
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=reservas

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Security Configuration (for Google authentication - future)
# SECRET_KEY=your-secret-key-here
# GOOGLE_CLIENT_ID=your-google-client-id
# GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### Step 2: Start Containers

```bash
# In the backend/ folder
docker compose up -d

# Check if containers are running
docker ps

# Should show:
# postgres-reservas (PostgreSQL on port 5432)
# reservas-api (FastAPI on port 8000)
```

### Step 3: Apply Database Migrations

```bash
# Apply all pending migrations
docker compose exec api alembic upgrade head

# Check migration status
docker compose exec api alembic current

# View migration history
docker compose exec api alembic history
```

### Step 4: Verify Health Check

```bash
# Check if API is responding
curl http://localhost:8000/health

# Should return:
# {"status": "healthy", "database": "connected"}
```

## 📚 Interactive Documentation

The API has automatic documentation generated by FastAPI:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🗂️ Project Structure

```
backend/
├── alembic/                 # Alembic migrations
│   ├── versions/            # Migration files
│   ├── env.py               # Alembic configuration
│   └── script.py.mako        # Template for new migrations
├── alembic.ini              # Alembic configuration
├── app/
│   ├── __init__.py
│   ├── main.py              # Main FastAPI application
│   ├── models.py            # SQLAlchemy models (Local, Sala, Reserva)
│   ├── schemas.py           # Pydantic schemas (validation)
│   ├── crud.py              # Database operations (CRUD)
│   ├── routes.py            # API endpoints
│   └── services/
│       └── database.py      # Database configuration
├── migrations/              # Manual SQL migrations (legacy)
├── docker-compose.yml       # Docker orchestration
├── Dockerfile               # API Docker image
├── pyproject.toml           # PDM dependencies
├── pdm.lock                 # Dependency lock
└── README.md                # This file
```

## 🛣️ API Endpoints

### Locations (`/api/v1/locais`)

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/api/v1/locais` | List locations | 200 |
| GET | `/api/v1/locais/{id}` | Get location by ID | 200/404 |
| POST | `/api/v1/locais` | Create new location | 201/400/409 |
| PUT | `/api/v1/locais/{id}` | Update location | 200/404/409 |
| PATCH | `/api/v1/locais/{id}` | Partial update | 200/404/409 |
| DELETE | `/api/v1/locais/{id}` | Delete location (soft delete) | 200/404 |

**Listing filters:**
- `skip`: number of records to skip (default: 0)
- `limit`: maximum number of records (default: 100, max: 1000)
- `ativo`: filter by active/inactive status (true/false)

### Rooms (`/api/v1/salas`)

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/api/v1/salas` | List rooms | 200 |
| GET | `/api/v1/salas/{id}` | Get room by ID | 200/404 |
| POST | `/api/v1/salas` | Create new room | 201/400/404/409 |
| PUT | `/api/v1/salas/{id}` | Update room | 200/404/409 |
| PATCH | `/api/v1/salas/{id}` | Partial update | 200/404/409 |
| DELETE | `/api/v1/salas/{id}` | Delete room (soft delete) | 200/404 |

**Listing filters:**
- `skip`: number of records to skip
- `limit`: maximum number of records
- `local_id`: filter by location ID
- `ativo`: filter by active/inactive status
- `capacidade_minima`: filter by minimum capacity

**Validations:**
- `local_id` must point to an active location
- `nome` must be unique within the same location
- `capacidade` if provided must be > 0

### Reservations (`/api/v1/reservas`)

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/api/v1/reservas` | List reservations | 200 |
| GET | `/api/v1/reservas/{id}` | Get reservation by ID | 200/404 |
| POST | `/api/v1/reservas` | Create new reservation | 201/400/404/409 |
| PUT | `/api/v1/reservas/{id}` | Update reservation | 200/404/409 |
| PATCH | `/api/v1/reservas/{id}` | Partial update | 200/404/409 |
| DELETE | `/api/v1/reservas/{id}` | Delete reservation (soft delete) | 200/404 |

**Listing filters:**
- `skip`: number of records to skip
- `limit`: maximum number of records
- `data_inicio`: start date/time of interval (ISO 8601)
- `data_fim`: end date/time of interval (ISO 8601)
- `sala`: filter by room name (partial search)
- `local`: filter by location name (partial search)
- `responsavel`: filter by responsible person (partial search)

**Validations:**
- `data_inicio` < `data_fim` (does not allow equal)
- Does not allow reservations in the past
- `local_id` and `sala_id` must point to active records
- The room must belong to the specified location
- Time conflict validation in the same room
- If `cafe = true`, `quantidade_cafe` is required and > 0

## 📋 Business Rules

### Soft Delete

All models (Local, Sala, Reserva) implement **soft delete**:
- When deleting, the `deleted_at` field is filled with the current date/time (UTC)
- Listing and search queries only consider records with `deleted_at IS NULL`
- Trying to fetch a deleted record returns `404 Not Found`

### Time Conflict

Two reservations conflict if:
- `nova_data_inicio < existente_data_fim` **AND**
- `nova_data_fim > existente_data_inicio`
- And they are for the **same room**

**Technical decision:** Adjacent times are allowed (e.g., 10:00-11:00 and 11:00-12:00).

### Dates and Timezone

- All dates are stored in **UTC** in the database
- The API receives dates in **ISO 8601** format (e.g., `2025-11-19T10:00:00Z`)
- Creating or updating reservations for the past is not allowed

### Coffee Rule

- If `cafe = true`: `quantidade_cafe` is required and must be > 0
- If `cafe = false` or not provided: `quantidade_cafe` is ignored/zeroed

## 🔧 Useful Commands

### Migrations (Alembic)

```bash
# Apply all pending migrations
docker compose exec api alembic upgrade head

# Create a new migration (after modifying models.py)
docker compose exec api alembic revision --autogenerate -m "Description of change"

# Revert to a previous migration
docker compose exec api alembic downgrade -1

# Revert all migrations
docker compose exec api alembic downgrade base

# View current status
docker compose exec api alembic current

# View migration history
docker compose exec api alembic history

# View SQL that will be executed (without applying)
docker compose exec api alembic upgrade head --sql
```

**Important:** Always review automatically generated migrations before applying them, especially when there are complex schema changes.

### Docker Compose

```bash
# Start services in background
docker compose up -d

# Stop services
docker compose down

# Stop and remove volumes (warning: deletes data)
docker compose down -v

# View logs in real time
docker compose logs -f api
docker compose logs -f db

# View logs from both
docker compose logs -f

# Restart only the API
docker compose restart api

# Rebuild API image
docker compose up -d --build api
```

### Database Access

```bash
# Access PostgreSQL via psql
docker compose exec db psql -U user -d reservas

# Useful psql commands:
# \l          - List databases
# \dt         - List tables
# \d+ reservas - View reservas table structure
# SELECT * FROM reservas; - View all reservations
```

### API Container Access

```bash
# Access container shell
docker compose exec api bash

# Run Python commands
docker compose exec api pdm run python -c "from app.models import Reserva; print('OK')"
```

## 🐛 Troubleshooting

### PostgreSQL Connection Error

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# View PostgreSQL logs
docker compose logs db

# Restart PostgreSQL
docker compose restart db
```

### Port 8000 Occupied

```bash
# Check processes on port 8000
sudo lsof -i :8000

# Or change the port in docker-compose.yml:
# ports:
#   - "8001:8000"  # Maps host port 8001 to container port 8000
```

### Error Creating Tables

```bash
# Check if migrations were applied
docker compose exec api alembic current

# Apply migrations manually
docker compose exec api alembic upgrade head

# Check API logs
docker compose logs api

# If necessary, recreate containers and volumes
docker compose down -v
docker compose up -d
# Then apply migrations again
docker compose exec api alembic upgrade head
```

### Health Check Failing

```bash
# Check if API is responding
curl http://localhost:8000/health

# Check logs
docker compose logs api

# Check container connectivity with database
docker compose exec api python -c "from app.services.database import engine; print(engine.connect())"
```

## 🧪 Usage Examples

### Create a Location

```bash
curl -X POST "http://localhost:8000/api/v1/locais" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Sede Principal",
    "descricao": "Prédio principal da empresa"
  }'
```

### Create a Room

```bash
curl -X POST "http://localhost:8000/api/v1/salas" \
  -H "Content-Type: application/json" \
  -d '{
    "local_id": 1,
    "nome": "Sala de Reuniões A",
    "capacidade": 10,
    "recursos": "TV, Projetor, Videoconferência"
  }'
```

### Create a Reservation

```bash
curl -X POST "http://localhost:8000/api/v1/reservas" \
  -H "Content-Type: application/json" \
  -d '{
    "local_id": 1,
    "sala_id": 1,
    "local": "Sede Principal",
    "sala": "Sala de Reuniões A",
    "data_inicio": "2025-12-01T10:00:00Z",
    "data_fim": "2025-12-01T11:00:00Z",
    "responsavel": "João Silva",
    "cafe": true,
    "quantidade_cafe": 10,
    "descricao": "Reunião de planejamento"
  }'
```

### List Reservations with Filters

```bash
# List reservations for a specific room
curl "http://localhost:8000/api/v1/reservas?sala=Sala%20de%20Reuniões%20A"

# List reservations in a date range
curl "http://localhost:8000/api/v1/reservas?data_inicio=2025-12-01T00:00:00Z&data_fim=2025-12-01T23:59:59Z"
```

## 📝 Documented Technical Decisions

### Reservations in the Past

**Decision:** Not allowed. When creating or updating a reservation, the system validates that `data_inicio >= now()`.

### Adjacent Times

**Decision:** Allowed. Reservations that end exactly when another starts are not considered a conflict (e.g., 10:00-11:00 and 11:00-12:00).

### Soft Delete

**Decision:** Implemented in all models. Deleted records do not appear in listings, but remain in the database for auditing.

### Denormalized Fields

**Decision:** The `Reserva` model maintains `local` and `sala` fields as denormalized strings, in addition to the FKs `local_id` and `sala_id`. This facilitates queries and maintains API compatibility, but requires manual synchronization.

## 🔐 Security (Future)

Google OAuth2 authentication is planned but not implemented. When implemented:

- Creation/edition/deletion endpoints will be protected
- Listing endpoints may remain public (read-only)
- It will be necessary to configure `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`

## 📄 License

This project is for educational purposes.
