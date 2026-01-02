from typing import List
from pydantic import BaseModel

class IngredientsItem(BaseModel):
    name: str
    quantity: str

class Recipe(BaseModel):
    name: str
    categories: List[str]
    ingredients: List[IngredientsItem]
    steps: List[str]
