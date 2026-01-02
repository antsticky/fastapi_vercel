import json
import base64
import os
import requests
from typing import Dict, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from api.DataModels.recipe import Recipe


# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "antsticky"
REPO_NAME = "fastapi_vercel"
FILE_PATH = "data/recipes.json"

API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"


recipes_db: Dict[int, Recipe] = {}
current_id = 1


def load_recipes_from_github():
    global recipes_db, current_id

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    try:
        response = requests.get(API_URL, headers=headers)
        print("GitHub GET status:", response.status_code)

        if response.status_code == 200:
            data = response.json()
            if "content" in data:
                decoded = base64.b64decode(data["content"]).decode()
                raw = json.loads(decoded)
                print("Loaded recipes from GitHub:", raw)
            else:
                print("GitHub response missing 'content':", data)
                raw = {}
        else:
            print("GitHub GET error:", response.text)
            raw = {}

    except Exception as e:
        print("Exception while loading from GitHub:", e)
        raw = {}

    try:
        recipes_db = {int(k): Recipe(**v) for k, v in raw.items()}
    except Exception as e:
        print("Error parsing recipes:", e)
        recipes_db = {}

    current_id = max(recipes_db.keys(), default=0) + 1


def save_recipes_to_github():
    try:
        content = json.dumps(
            {rid: recipe.dict() for rid, recipe in recipes_db.items()},
            indent=4
        )
        encoded = base64.b64encode(content.encode()).decode()

        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }

        sha = None
        sha_response = requests.get(API_URL, headers=headers)
        print("GitHub SHA status:", sha_response.status_code)

        if sha_response.status_code == 200:
            sha_data = sha_response.json()
            sha = sha_data.get("sha")
            print("Existing SHA:", sha)
        else:
            print("SHA lookup failed:", sha_response.text)

        payload = {
            "message": "Update recipes.json",
            "content": encoded,
            "sha": sha
        }

        put_response = requests.put(API_URL, headers=headers, json=payload)
        print("GitHub PUT status:", put_response.status_code)
        print("GitHub PUT response:", put_response.text)

        return put_response.json()

    except Exception as e:
        print("Exception while saving to GitHub:", e)
        return {"error": str(e)}


# Load recipes at startup
load_recipes_from_github()


# -----------------------------
# API Routes
# -----------------------------
@app.get("/")
def hello():
    return {"message": "Hello from FastAPI!"}


@app.get("/ping")
def ping():
    return {"message": "pong"}


@app.get("/recipe")
def get_all_recipes():
    return recipes_db


@app.get("/recipe/{recipe_id}")
def get_recipe(recipe_id: int):
    if recipe_id not in recipes_db:
        return {"error": "Recipe not found"}
    return recipes_db[recipe_id]


@app.post("/recipe")
def create_recipe(recipe: Recipe):
    global current_id

    recipes_db[current_id] = recipe
    save_recipes_to_github()

    response = {"id": current_id, "message": "Recipe created successfully"}
    current_id += 1
    return response
