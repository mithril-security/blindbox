import uvicorn
from fastapi import FastAPI
import requests


app = FastAPI()


@app.get("/hello")
def hello() -> str:
    return "Hello World"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
