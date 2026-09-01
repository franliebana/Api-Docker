# API Docker

A simple FastAPI application containerized with Docker and deployed to Render.

## Overview

This project exposes a minimal REST API that returns a health/status message. It can be run locally with Docker or directly with Python, and it is also configured for CI with GitHub Actions and continuous deployment with Render.

## Requirements

- Docker
- Python 3.10 or newer (optional, for local non-Docker execution)
- GitHub account with GitHub Actions enabled
- Render account for deployment

## Run with Docker

Build the image:

```bash
docker build -t api-docker .
```

Start the container:

```bash
docker run --rm -p 8000:8000 api-docker
```

The API will be available at <http://localhost:8000>.

## Available endpoint

### `GET /`

Returns a simple status message to verify the API is working:

```json
{
  "status": "ok",
  "message": "Probando el sistema completo"
}
```

You can test it with:

```bash
curl http://localhost:8000/
```

FastAPI interactive documentation is available at <http://localhost:8000/docs>.

## Run locally without Docker

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies and start the server:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

To deactivate the virtual environment:

```bash
deactivate
```

## CI/CD

### Continuous Integration

A GitHub Actions workflow is configured in [.github/workflows/ci.yaml](.github/workflows/ci.yaml). It runs on pushes to the `main` branch and validates the Docker build.

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
├── Dockerfile
├── main.py
├── README.md
├── requirements.txt
└── .gitignore
```

## Useful commands

```bash
# Build Docker image
docker build -t api-docker .

# Run container
docker run --rm -p 8000:8000 api-docker

# Run locally with uvicorn
uvicorn main:app --reload
```

## Notes

This project is intended as a minimal example of combining FastAPI, Docker, GitHub Actions, and Render for a simple API deployment workflow.