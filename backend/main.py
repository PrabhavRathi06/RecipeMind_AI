import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import crud
import schemas
from database import engine, get_db
from scraper import scrape_recipe_page, extract_recipe_from_jsonld
from llm import extract_recipe_with_llm, generate_meal_plan

# setup app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create all DB tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RecipeMind AI API",
    description="Extract, analyze, and manage recipes using AI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# health check endpoints

@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "RecipeMind AI API is running"}

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


# extract recipe endpoints

@app.post("/api/extract", response_model=schemas.ExtractResponse, tags=["Recipes"])
def extract_recipe(request: schemas.ExtractRequest, db: Session = Depends(get_db)):
    # scrape url, extract data with gemini, and save to db
    url = request.url.strip()

    # Validate URL format
    if not url.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="URL must start with http:// or https://"
        )

    # Check if already processed (cache hit)
    existing = crud.get_recipe_by_url(db, url)
    if existing:
        logger.info(f"Cache hit for URL: {url}")
        return schemas.ExtractResponse(
            success=True,
            message="Recipe loaded from cache",
            recipe=schemas.RecipeDetail.model_validate(existing),
            cached=True,
        )

    # Step 1: Scrape the page
    logger.info(f"Scraping URL: {url}")
    try:
        scraped = scrape_recipe_page(url)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

    # Step 2: Extract via LLM
    logger.info("Extracting recipe with LLM...")
    try:
        llm_data = extract_recipe_with_llm(scraped["cleaned_text"], url)
    except ValueError as e:
        msg = str(e)
        # If Gemini quota/rate-limit is hit, fall back to JSON-LD extraction.
        if "429" in msg or "quota" in msg.lower() or "resourceexhausted" in msg.lower():
            logger.warning("LLM quota exceeded; trying JSON-LD fallback extraction.")
            fallback = extract_recipe_from_jsonld(scraped.get("raw_html", ""), url)
            if fallback:
                llm_data = fallback
            else:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Gemini quota exceeded and JSON-LD fallback was not available for this page."
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=msg
            )

    # Step 3: Save to database
    try:
        recipe = crud.create_recipe_from_llm(
            db=db,
            url=url,
            raw_html=scraped["raw_html"],
            llm_data=llm_data,
        )
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save recipe to database: {str(e)}"
        )

    message = "Recipe extracted and saved successfully"
    if isinstance(llm_data, dict) and llm_data.get("_extraction_method") == "jsonld":
        message = "Recipe extracted using JSON-LD fallback (Gemini quota exceeded)"

    return schemas.ExtractResponse(
        success=True,
        message=message,
        recipe=schemas.RecipeDetail.model_validate(recipe),
        cached=False,
    )


# history endpoints

@app.get("/api/recipes", response_model=schemas.HistoryResponse, tags=["Recipes"])
def get_recipes(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    # get all saved recipes
    recipes = crud.get_all_recipes(db, skip=skip, limit=limit)
    total = crud.count_recipes(db)
    return schemas.HistoryResponse(
        success=True,
        recipes=[schemas.RecipeListItem.model_validate(r) for r in recipes],
        total=total,
    )


@app.get("/api/recipes/{recipe_id}", response_model=schemas.ExtractResponse, tags=["Recipes"])
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    # get single recipe
    recipe = crud.get_recipe_by_id(db, recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} not found"
        )
    return schemas.ExtractResponse(
        success=True,
        message="Recipe retrieved successfully",
        recipe=schemas.RecipeDetail.model_validate(recipe),
    )


@app.delete("/api/recipes/{recipe_id}", tags=["Recipes"])
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    # delete recipe
    deleted = crud.delete_recipe(db, recipe_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe with id {recipe_id} not found"
        )
    return {"success": True, "message": f"Recipe {recipe_id} deleted"}


# meal planner endpoints

@app.post("/api/meal-plan", response_model=schemas.MealPlanResponse, tags=["Meal Planner"])
def create_meal_plan(request: schemas.MealPlanRequest, db: Session = Depends(get_db)):
    # generate shopping list from selected recipes
    if not (2 <= len(request.recipe_ids) <= 5):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Please select between 2 and 5 recipes for a meal plan"
        )

    recipes = []
    titles = []
    for rid in request.recipe_ids:
        recipe = crud.get_recipe_by_id(db, rid)
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recipe {rid} not found"
            )
        titles.append(recipe.title or f"Recipe #{rid}")
        recipes.append({
            "title": recipe.title,
            "ingredients": [
                {"quantity": i.quantity, "unit": i.unit, "item": i.item}
                for i in recipe.ingredients
            ]
        })

    try:
        meal_plan_data = generate_meal_plan(recipes)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    return schemas.MealPlanResponse(
        success=True,
        recipe_titles=titles,
        combined_shopping_list=meal_plan_data.get("combined_shopping_list", {}),
    )
