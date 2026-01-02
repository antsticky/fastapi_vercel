import json
from pathlib import Path
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.DataModels.recipe import Recipe

import json
import base64
import os
import requests
from typing import Dict, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# GitHub Storage Config
# -----------------------------
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "antsticky"
REPO_NAME = "fastapi_vercel"
FILE_PATH = "data/recipes.json"

API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"


# -----------------------------
# In-memory DB
# -----------------------------
recipes_db: Dict[int, Recipe] = {}
current_id = 1


# -----------------------------
# GitHub Helpers
# -----------------------------
def load_recipes_from_github():
    global recipes_db, current_id

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(API_URL, headers=headers)

    if response.status_code == 200:
        content = response.json()["content"]
        decoded = base64.b64decode(content).decode()
        raw = json.loads(decoded)
    else:
        raw = {}

    recipes_db = {int(k): Recipe(**v) for k, v in raw.items()}

    current_id = max(recipes_db.keys(), default=0) + 1


def save_recipes_to_github():
    content = json.dumps(
        {rid: recipe.dict() for rid, recipe in recipes_db.items()},
        indent=4
    )
    encoded = base64.b64encode(content.encode()).decode()

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    # Get SHA for update
    sha = None
    sha_response = requests.get(API_URL, headers=headers)
    if sha_response.status_code == 200:
        sha = sha_response.json()["sha"]

    payload = {
        "message": "Update recipes.json",
        "content": encoded,
        "sha": sha
    }

    return requests.put(API_URL, headers=headers, json=payload).json()


# Load recipes at cold start
load_recipes_from_github()


# -----------------------------
# API Routes
# -----------------------------
@app.get("/")
def hello():
    return {"message": "Hello from Vercel FastAPI!"}


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


# -----------------------------
# Vercel Handler
# -----------------------------
handler = Mangum(app)
