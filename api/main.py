from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello World from FastAPI on Vercel!"}

@app.get("/sane")
def hello():
    return {"message": "I am working sane!"}
