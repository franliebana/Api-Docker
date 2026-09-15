from fastapi import FastAPI

from routers.users import router as users_router

# Main FastAPI application.
app = FastAPI()

app.include_router(users_router)

# Basic endpoint used to check that the API is running.
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Testing CI/CD pipeline with FastAPI"}