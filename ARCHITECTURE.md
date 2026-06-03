# System Architecture

## Overview
Production-grade web service architecture designed for horizontal scalability, security, and observability.

## Stack
- **Backend**: Python 3.11+ with FastAPI (async REST API)
- **Database**: PostgreSQL 15+ with connection pooling
- **Migrations**: Alembic
- **Auth**: JWT (HS256) + bcrypt password hashing
- **Frontend**: Vue 3 SPA with Vite, Pinia state, Vue Router
- **Infra**: Docker, docker-compose, Nginx reverse proxy

## Components

### API Service (FastAPI)
- Async request handling via uvicorn/uvloop
- Versioned routes: `/api/v1/...`
- Dependency injection for DB sessions and current user
- OpenAPI auto-generated at `/api/v1/docs`

### Middleware Stack
1. Request ID injection (`X-Request-ID`)
2. Structured JSON logging
3. CORS with configurable origins
4. GZip compression
5. Global exception handler
6. Authentication (JWT bearer)

### Data Layer
- PostgreSQL primary store
- SQLAlchemy 2.0 async ORM
- Connection pool sized for workers
- Indexes on all FKs and high-cardinality columns
- Alembic for schema versioning
- Staging migration mode for zero-downtime deploys

### Security
- HS256 JWT with 30-min access + 7-day refresh tokens
- bcrypt password hashing (cost factor 12)
- Pydantic input validation
- SQL injection prevention via ORM parameterization
- CORS allowlist

### Frontend
- SPA bundled by Vite
- Pinia for state management
- Vue Router with route guards
- Axios client with interceptors for auth
- Responsive design via CSS Grid + custom properties

## Data Flow
