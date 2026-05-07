import json
import re
import logging
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from database import settings

logger = logging.getLogger(__name__)

# llm init

def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.3,
    )


# prompt templates
import os

PROMPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")

def load_prompt(filename: str) -> str:
    with open(os.path.join(PROMPTS_DIR, filename), "r", encoding="utf-8") as f:
        return f.read()

# Load prompts directly from the text files required by the assignment
EXTRACTION_PROMPT = load_prompt("recipe_extraction.txt")
MEAL_PLAN_PROMPT = load_prompt("meal_planning.txt")


# core functions

def extract_recipe_with_llm(page_content: str, url: str) -> dict:
    # send scraped text to gemini and return json
    llm = get_llm()
    
    # replace variables manually to avoid crashing on the JSON schema curly braces
    formatted_prompt = EXTRACTION_PROMPT.replace("{page_content}", page_content).replace("{url}", url)
    
    prompt = ChatPromptTemplate.from_messages([
        ("human", "{text}")
    ])
    chain = prompt | llm | StrOutputParser()

    logger.info(f"Sending content to LLM for URL: {url}")

    try:
        raw_output = chain.invoke({"text": formatted_prompt})
    except Exception as e:
        raise ValueError(f"LLM request failed: {str(e)}")

    # Parse JSON from response
    parsed = _parse_json_response(raw_output)
    if not parsed:
        raise ValueError("LLM returned invalid or empty JSON")

    # Validate required fields
    if not parsed.get("title"):
        raise ValueError("LLM could not extract a recipe title — ensure the URL points to a recipe page")

    logger.info(f"Successfully extracted recipe: {parsed.get('title')}")
    return parsed


def generate_meal_plan(recipes: list) -> dict:
    # combine ingredients from recipes into a shopping list
    llm = get_llm()

    # Build a summary of all recipes and their ingredients
    summaries = []
    for r in recipes:
        ingredients_text = ", ".join(
            f"{i.get('quantity', '')} {i.get('unit', '')} {i.get('item', '')}".strip()
            for i in r.get("ingredients", [])
        )
        summaries.append(f"Recipe: {r.get('title', 'Unknown')}\nIngredients: {ingredients_text}")

    recipes_summary = "\n\n".join(summaries)
    
    # replace manually to avoid crashing on json curly braces
    formatted_prompt = MEAL_PLAN_PROMPT.replace("{recipes_summary}", recipes_summary)

    prompt = ChatPromptTemplate.from_messages([
        ("human", "{text}")
    ])
    chain = prompt | llm | StrOutputParser()

    try:
        raw_output = chain.invoke({"text": formatted_prompt})
    except Exception as e:
        raise ValueError(f"LLM meal plan request failed: {str(e)}")

    parsed = _parse_json_response(raw_output)
    if not parsed:
        raise ValueError("LLM returned invalid JSON for meal plan")

    return parsed


# helpers

def _parse_json_response(text: str) -> Optional[dict]:
    # parse the json block from the gemini string
    if not text:
        return None

    # Remove markdown code fences if present
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON block inside the text
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    logger.error(f"Failed to parse JSON from LLM response: {text[:500]}")
    return None
