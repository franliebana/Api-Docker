# API Docker

API sencilla creada con FastAPI y ejecutada con Uvicorn dentro de Docker.

## Requisitos

- Docker
- Python 3.10 o posterior para ejecutarla sin Docker

## Ejecutar con Docker

Construye la imagen:

```bash
docker build -t api-docker .
```

Inicia el contenedor:

```bash
docker run --rm -p 8000:8000 api-docker
```

La API estará disponible en <http://localhost:8000>.

## Endpoint disponible

### `GET /`

Devuelve un mensaje para comprobar que la API está funcionando:

```json
{
  "status": "ok",
  "message": "Mi primer contenedor levantado"
}
```

Puedes probarlo con:

```bash
curl http://localhost:8000/
```

La documentación interactiva de FastAPI está disponible en <http://localhost:8000/docs>.

## Ejecutar localmente

Crea y activa un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instala las dependencias y arranca el servidor:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Para salir del entorno virtual:

```bash
deactivate
```

## Estructura

```text
.
├── Dockerfile
├── main.py
├── README.md
└── requirements.txt
```