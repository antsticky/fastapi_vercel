from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello World from Vercel!"}

@app.get("/sane")
def hello():
    return {"message": "I am working sane!"}

@app.get("/ping")
def hello():
    return {"message": "pong"}
