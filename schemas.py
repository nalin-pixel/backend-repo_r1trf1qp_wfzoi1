"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Add your own schemas here:
# --------------------------------------------------

class NutritionFacts(BaseModel):
    calories: float = Field(0, ge=0, description="Calories (kcal)")
    protein: float = Field(0, ge=0, description="Protein (g)")
    carbs: float = Field(0, ge=0, description="Carbohydrates (g)")
    fat: float = Field(0, ge=0, description="Fat (g)")

class IngredientItem(BaseModel):
    name: str = Field(..., description="Ingredient name, e.g., 'Chicken Breast'")
    quantity: float = Field(1, ge=0, description="Quantity for the ingredient")
    unit: str = Field("unit", description="Unit of measure, e.g., g, ml, cups")
    nutrition: Optional[NutritionFacts] = Field(default_factory=NutritionFacts)

class Recipe(BaseModel):
    """
    Recipes collection schema
    Collection name: "recipe"
    """
    title: str = Field(..., description="Recipe title")
    description: Optional[str] = Field(None, description="Short description")
    servings: int = Field(1, ge=1, description="Number of servings")
    tags: List[str] = Field(default_factory=list, description="Tags like dinner, vegan")
    ingredients: List[IngredientItem] = Field(default_factory=list)
    instructions: List[str] = Field(default_factory=list, description="Step-by-step instructions")
    total_nutrition: Optional[NutritionFacts] = None
    image_url: Optional[str] = None

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
