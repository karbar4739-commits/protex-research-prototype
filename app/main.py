from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {
        "system": "PROTEX Research Prototype",
        "status": "active"
    }