import uvicorn
from fastapi import FastAPI

# initialize our application
app = FastAPI()

# use fastapi decorator to turn our Hello World function into API endpoints
@app.get("/hello")
def hello() -> str:
    return "Hello World"

if __name__ == "__main__":
    # deploy our API on port 80
    uvicorn.run(app, host="0.0.0.0", port=80)


