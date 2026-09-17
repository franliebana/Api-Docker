# API Docker

A simple FastAPI application containerized with Docker and deployed to Render.

## Overview

This project exposes a FastAPI REST API with a PostgreSQL database. It currently includes user creation, user lookup, user deletion, and project CRUD operations, with password hashing and database migrations managed by Alembic. Both the API and PostgreSQL run through Docker Compose.

## Requirements

- Docker
- Python 3.10 or newer (optional, for local non-Docker execution)
- PostgreSQL (provided locally through Docker Compose)
- GitHub account with GitHub Actions enabled
- Render account for deployment

## Run with Docker

Start the API and PostgreSQL database:

```bash
docker compose up --build -d
```

The database uses the following local defaults:

```text
Database: api_docker
User: postgres
Password: postgres
Host: localhost
Port: 5432
```

Check that PostgreSQL is ready:

```bash
docker compose ps
docker compose exec db pg_isready -U postgres -d api_docker
```

The API will be available at <http://localhost:8000> and PostgreSQL at `localhost:5432`.

View the API logs:

```bash
docker compose logs -f api
```

To stop the database while keeping its data:

```bash
docker compose stop db
```

To stop it and delete the stored data:

```bash
docker compose down -v
```

Build the image:

```bash
docker build -t api-docker .
```

Start the container:

```bash
docker run --rm -p 8000:8000 api-docker
```

The API will be available at <http://localhost:8000>.

## Available endpoints

### `GET /`

Returns a simple status message to verify the API is working:

```json
{
  "status": "ok",
  "message": "CI/CD pipeline with FastAPI"
}
```

You can test it with:

```bash
curl http://localhost:8000/
```

FastAPI interactive documentation is available at <http://localhost:8000/docs>.

### Authentication

Login with email and password to receive a JWT token:

```text
POST /login
```

```json
{
  "email": "user@example.com",
  "password": "secret123"
}
```

Response:

```json
{
  "access_token": "<jwt-token>",
  "token_type": "bearer"
}
```

Use the token in the `Authorization` header for protected routes:

```http
Authorization: Bearer <jwt-token>
```

### Users

Create a user:

```text
POST /users
```

```json
{
  "email": "user@example.com",
  "password": "secret123"
}
```

List users:

```text
GET /users
```

Get one user:

```text
GET /users/{user_id}
```

Delete one user:

```text
DELETE /users/{user_id}
```

Passwords are stored as secure hashes and are never included in API responses.

### Projects

The project endpoints require authentication. Each project belongs to the authenticated user.

Create a project:

```text
POST /projects
```

```json
{
  "name": "My project",
  "description": "Project description"
}
```

List projects:

```text
GET /projects
```

Get one project:

```text
GET /projects/{project_id}
```

Update a project:

```text
PATCH /projects/{project_id}
```

Delete a project:

```text
DELETE /projects/{project_id}
```

## Run locally without Docker

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies and start the server locally:

```bash
pip install -r requirements.txt -r requirements-dev.txt
uvicorn main:app --reload
```

When running the API outside Docker, PostgreSQL must still be running and the default database URL uses `localhost`.

The application uses this local database URL by default:

```text
postgresql+psycopg://postgres:postgres@localhost:5432/api_docker
```

Apply database migrations before starting the API:

```bash
alembic upgrade head
```

Alternatively, use the project virtual environment explicitly:

```bash
.venv/bin/python -m alembic upgrade head
```

Run tests with `pytest`:

```bash
pytest
```

To run a specific test with more detail:

```bash
pytest -v tests/test_main.py
```

To deactivate the virtual environment:

```bash
deactivate
```

## CI/CD

### Continuous Integration

A GitHub Actions workflow is configured in [.github/workflows/ci.yaml](.github/workflows/ci.yaml). It runs on pushes to the `main` branch, installs the application and development dependencies, runs the tests, and validates the Docker build.

### Continuous Deployment

The application is deployed on Render using the public URL:

https://api-docker-epwx.onrender.com/

This deployment is configured to build and launch the app from the repository automatically after changes are pushed to the deployment branch.

## Project structure

```text
.
├── .github/
│   └── workflows/
│       └── ci.yaml
├── alembic/
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions/
│       └── f22fe3ed6021_create_users_and_projects.py
├── alembic.ini
├── database.py
├── Dockerfile
├── docker-compose.yml
├── main.py
├── models.py
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── routers/
│   ├── __init__.py
│   ├── auth.py
│   ├── project.py
│   └── users.py
├── schemas.py
├── tests/
│   └── test_main.py
├── .gitignore
└── .dockerignore
```

## Useful commands

```bash
# Build Docker image
docker build -t api-docker .

# Run container
docker run --rm -p 8000:8000 api-docker

# Run the API and database with Docker Compose
docker compose up --build -d

# Run the API locally with uvicorn
uvicorn main:app --reload

# Run tests
python -m pytest

# Apply database migrations
alembic upgrade head

# Show database row counts
docker compose exec db psql -U postgres -d api_docker -c "SELECT COUNT(*) FROM users; SELECT COUNT(*) FROM projects;"
```

## Notes

This project is an example of a FastAPI application with PostgreSQL, SQLAlchemy, Alembic, Docker, JWT authentication, GitHub Actions, and Render deployment. The database currently contains `users` and `projects` tables, and project access is restricted to the authenticated user.