# MockEngine Backend

FastAPI backend for the MockEngine mobile SDK - a mock engine that allows developers to create interception rules for mocking HTTP responses during development and testing.

## Tech Stack

- **FastAPI** - Modern async web framework
- **SQLite** - Lightweight database
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migration tool
- **Pydantic** - Data validation
- **Pytest** - Testing framework

## Setup

1. Create and activate virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize database:
```bash
alembic upgrade head
```

4. Run the server:
```bash
uvicorn src.main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

Run tests:
```bash
pytest -v
```

## API Endpoints

### Management API (No Authentication)

- `POST /api/v1/api-keys` - Generate SDK API Key
- `POST /api/v1/rules` - Create Interception Rule
- `GET /api/v1/rules` - Fetch All Rules
- `DELETE /api/v1/rules/{id}` - Delete Rule
- `PUT /api/v1/rules/{id}` - Update/Disable Rule

### SDK API (Requires `X-API-KEY` Header)

- `GET /api/sdk/config` - Get Active Rules for SDK
- `POST /api/sdk/register` - Register Device
- `POST /api/sdk/log-intercept` - Log Interception Event
- `POST /api/sdk/log-call` - Log Any API Call (Analytics)

## Database Schema

- `api_keys` - API key management
- `rules` - Interception rules
- `devices` - Device registrations
- `call_logs` - API call analytics
- `interception_logs` - Interception event logs
