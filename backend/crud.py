from sqlalchemy.orm import Session
from typing import Optional, List
import models
import schemas


# recipe crud

def get_recipe_by_url(db: Session, url: str) -> Optional[models.Recipe]:
    return db.query(models.Recipe).filter(models.Recipe.url == url).first()


def get_recipe_by_id(db: Session, recipe_id: int) -> Optional[models.Recipe]:
    return db.query(models.Recipe).filter(models.Recipe.id == recipe_id).first()


def get_all_recipes(db: Session, skip: int = 0, limit: int = 100) -> List[models.Recipe]:
    return (
        db.query(models.Recipe)
        .order_by(models.Recipe.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def count_recipes(db: Session) -> int:
    return db.query(models.Recipe).count()


def create_recipe_from_llm(db: Session, url: str, raw_html: str, llm_data: dict) -> models.Recipe:
    """
    Persist a fully extracted recipe and all related data to the database.
    """
    # Create the parent Recipe record
    recipe = models.Recipe(
        url=url,
        title=llm_data.get("title"),
        cuisine=llm_data.get("cuisine"),
        difficulty=llm_data.get("difficulty"),
        prep_time=llm_data.get("prep_time"),
        cook_time=llm_data.get("cook_time"),
        total_time=llm_data.get("total_time"),
        servings=llm_data.get("servings"),
        raw_html=raw_html,
    )
    db.add(recipe)
    db.flush()  # Get the recipe ID before adding children

    # Ingredients
    for ing in llm_data.get("ingredients", []):
        if ing.get("item"):
            db.add(models.Ingredient(
                recipe_id=recipe.id,
                quantity=ing.get("quantity"),
                unit=ing.get("unit"),
                item=ing.get("item"),
            ))

    # Instructions
    for inst in llm_data.get("instructions", []):
        if inst.get("instruction_text"):
            db.add(models.Instruction(
                recipe_id=recipe.id,
                step_number=inst.get("step_number", 0),
                instruction_text=inst.get("instruction_text"),
            ))

    # Nutrition
    nutrition_data = llm_data.get("nutrition")
    if nutrition_data:
        db.add(models.Nutrition(
            recipe_id=recipe.id,
            calories=nutrition_data.get("calories"),
            protein=nutrition_data.get("protein"),
            carbs=nutrition_data.get("carbs"),
            fat=nutrition_data.get("fat"),
        ))

    # Substitutions
    for sub in llm_data.get("substitutions", []):
        if sub.get("original") and sub.get("replacement"):
            db.add(models.Substitution(
                recipe_id=recipe.id,
                original=sub.get("original"),
                replacement=sub.get("replacement"),
                reason=sub.get("reason"),
            ))

    # Shopping list
    for item in llm_data.get("shopping_list", []):
        if item.get("item") and item.get("category"):
            db.add(models.ShoppingListItem(
                recipe_id=recipe.id,
                category=item.get("category"),
                item=item.get("item"),
            ))

    # Related recipes
    for related in llm_data.get("related_recipes", []):
        if related.get("title"):
            db.add(models.RelatedRecipe(
                recipe_id=recipe.id,
                title=related.get("title"),
                description=related.get("description"),
                suggested_url=related.get("suggested_url"),
            ))

    db.commit()
    db.refresh(recipe)
    return recipe


def delete_recipe(db: Session, recipe_id: int) -> bool:
    recipe = get_recipe_by_id(db, recipe_id)
    if recipe:
        db.delete(recipe)
        db.commit()
        return True
    return False
