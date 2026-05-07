from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime


# request schemas

class ExtractRequest(BaseModel):
    url: str

class MealPlanRequest(BaseModel):
    recipe_ids: List[int]


# sub-schemas

class IngredientSchema(BaseModel):
    quantity: Optional[str] = None
    unit: Optional[str] = None
    item: str

    class Config:
        from_attributes = True


class InstructionSchema(BaseModel):
    step_number: int
    instruction_text: str

    class Config:
        from_attributes = True


class NutritionSchema(BaseModel):
    calories: Optional[str] = None
    protein: Optional[str] = None
    carbs: Optional[str] = None
    fat: Optional[str] = None

    class Config:
        from_attributes = True


class SubstitutionSchema(BaseModel):
    original: str
    replacement: str
    reason: Optional[str] = None

    class Config:
        from_attributes = True


class ShoppingListItemSchema(BaseModel):
    category: str
    item: str

    class Config:
        from_attributes = True


class RelatedRecipeSchema(BaseModel):
    title: str
    description: Optional[str] = None
    suggested_url: Optional[str] = None

    class Config:
        from_attributes = True


# recipe schemas

class RecipeBase(BaseModel):
    url: str
    title: Optional[str] = None
    cuisine: Optional[str] = None
    difficulty: Optional[str] = None
    prep_time: Optional[str] = None
    cook_time: Optional[str] = None
    total_time: Optional[str] = None
    servings: Optional[str] = None


class RecipeListItem(RecipeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RecipeDetail(RecipeBase):
    id: int
    created_at: datetime
    ingredients: List[IngredientSchema] = []
    instructions: List[InstructionSchema] = []
    nutrition: Optional[NutritionSchema] = None
    substitutions: List[SubstitutionSchema] = []
    shopping_list: List[ShoppingListItemSchema] = []
    related_recipes: List[RelatedRecipeSchema] = []

    class Config:
        from_attributes = True


class ExtractResponse(BaseModel):
    success: bool
    message: str
    recipe: Optional[RecipeDetail] = None
    cached: bool = False


class HistoryResponse(BaseModel):
    success: bool
    recipes: List[RecipeListItem]
    total: int


class MealPlanResponse(BaseModel):
    success: bool
    recipe_titles: List[str]
    combined_shopping_list: dict  # { category: [items] }
