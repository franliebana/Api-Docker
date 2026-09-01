from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Testing CI/CD pipeline with FastAPI"}