from typing import Union, List
from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()

class Item(BaseModel):
    name: str

# In-memory storage for uploaded items
items_store = []

@app.get("/api/")
def default():
    # Return the in-memory items
    return {"items": items_store}

@app.post("/api/upload")
def upload(item: Item):
    # Store the item in the in-memory structure
    items_store.append(item.dict())
    return {"name": item.name, "status": "stored"}