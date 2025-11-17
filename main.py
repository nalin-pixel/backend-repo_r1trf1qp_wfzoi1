import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Recipe, IngredientItem, NutritionFacts

app = FastAPI(title="Recipes API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Recipes & Nutrition API is running"}

@app.get("/schema")
def get_schema():
    # Expose schemas so UI tools can introspect
    return {
        "collections": [
            "recipe",
            "user",
            "product"
        ]
    }

class RecipeCreate(BaseModel):
    title: str
    description: Optional[str] = None
    servings: int = 1
    tags: List[str] = []
    ingredients: List[IngredientItem] = []
    instructions: List[str] = []
    image_url: Optional[str] = None

@app.post("/api/recipes")
def create_recipe(payload: RecipeCreate):
    try:
        # compute simple total nutrition from ingredients if provided
        total = NutritionFacts()
        for ing in payload.ingredients:
            if ing.nutrition:
                total.calories += ing.nutrition.calories
                total.protein += ing.nutrition.protein
                total.carbs += ing.nutrition.carbs
                total.fat += ing.nutrition.fat
        recipe = Recipe(
            title=payload.title,
            description=payload.description,
            servings=payload.servings,
            tags=payload.tags,
            ingredients=payload.ingredients,
            instructions=payload.instructions,
            total_nutrition=total,
            image_url=payload.image_url,
        )
        inserted_id = create_document("recipe", recipe)
        return {"id": inserted_id, "message": "Recipe created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/recipes")
def list_recipes(limit: int = 50):
    try:
        docs = get_documents("recipe", limit=limit)
        # convert ObjectId to string if present
        for d in docs:
            if "_id" in d:
                d["id"] = str(d.pop("_id"))
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
