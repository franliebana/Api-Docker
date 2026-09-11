from fastapi import FastAPI

# Main FastAPI application.
app = FastAPI()

# Basic endpoint used to check that the API is running.
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Testing CI/CD pipeline with FastAPI"}