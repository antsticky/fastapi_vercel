import json
from pathlib import Path
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.DataModels.recipe import Recipe

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = Path("data/recipes.json")

recipes_db: Dict[int, Recipe] = {}
current_id = 1


def load_recipes():
    global recipes_db, current_id

    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        DATA_FILE.write_text("{}")  # create empty file

    with open(DATA_FILE, "r") as f:
        raw = json.load(f)

    recipes_db = {int(k): Recipe(**v) for k, v in raw.items()}

    if recipes_db:
        current_id = max(recipes_db.keys()) + 1
    else:
        current_id = 1


def save_recipes():
    with open(DATA_FILE, "w") as f:
        json.dump(
            {rid: recipe.dict() for rid, recipe in recipes_db.items()},
            f,
            indent=4
        )


load_recipes()


@app.get("/")
def hello():
    return {"message": "Hello World from Local!"}


@app.get("/sane")
def sane():
    return {"message": "I am working sane!"}


@app.get("/ping")
def ping():
    return {"message": "pong"}


@app.post("/recipe")
def create_recipe(recipe: Recipe):
    global current_id
    recipes_db[current_id] = recipe
    save_recipes()
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
