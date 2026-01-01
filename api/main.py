from fastapi import FastAPI
from typing import Dict
from api.DataModels.recipe import Recipe

app = FastAPI()

recipes_db: Dict[int, Recipe] = {}
current_id = 1


@app.get("/")
def hello():
    from time import sleep

    sleep(2)
    return {"message": "Hello World from Local!"}


@app.get("/sane")
def hello():
    return {"message": "I am working sane!"}


@app.get("/ping")
def hello():
    return {"message": "pong"}


@app.post("/recipe")
def create_recipe(recipe: Recipe):
    global current_id
    recipes_db[current_id] = recipe
    response = {"id": current_id, "message": "Recipe created successfully"}
    current_id += 1
    return response


@app.get("/recipe/{recipe_id}")
def get_recipe(recipe_id: int):
    if recipe_id not in recipes_db:
        return {"error": "Recipe not found"}
    return recipes_db[recipe_id]


@app.get("/recipe")
def get_all_recipes():
    return recipes_db
