import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urlparse
import json
from typing import Any, Optional

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def scrape_recipe_page(url: str) -> dict:
    # get html from url and extract text
    def _fetch(u: str) -> requests.Response:
        return requests.get(u, headers=HEADERS, timeout=20, allow_redirects=True)

    def _jina_fallback(u: str) -> str | None:
        """
        Some sites (Cloudflare, bot protection) block plain HTTP clients.
        As a best-effort fallback, we try fetching the readable version via r.jina.ai.
        """
        parsed = urlparse(u)
        if parsed.scheme not in ("http", "https"):
            return None
        # r.jina.ai expects the full original URL appended after the scheme separator
        # Example: https://r.jina.ai/https://example.com/page
        return f"https://r.jina.ai/{parsed.scheme}://{parsed.netloc}{parsed.path}" + (
            f"?{parsed.query}" if parsed.query else ""
        )

    try:
        response = _fetch(url)

        # If blocked or not found, try a best-effort fallback.
        if response.status_code != 200:
            server = (response.headers.get("server") or "").lower()
            blocked_codes = {403, 429, 460, 500, 503}
            if response.status_code in blocked_codes or "cloudflare" in server:
                fallback_url = _jina_fallback(url)
                if fallback_url:
                    fallback_resp = _fetch(fallback_url)
                    if fallback_resp.status_code == 200 and fallback_resp.text.strip():
                        response = fallback_resp

        response.raise_for_status()
    except requests.exceptions.MissingSchema:
        raise ValueError(f"Invalid URL format: {url}")
    except requests.exceptions.ConnectionError:
        raise ValueError(f"Could not connect to: {url}")
    except requests.exceptions.HTTPError as e:
        status = getattr(e.response, "status_code", None)
        if status == 404:
            raise ValueError(
                "This page returned 404 (Not Found). Please double-check the recipe URL in your browser."
            )
        if status in (403, 429, 460):
            raise ValueError(
                "This site blocked automated access (bot protection). Try a different recipe URL/site, or use a URL that loads without requiring cookies/login."
            )
        raise ValueError(f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to fetch URL: {str(e)}")

    raw_html = response.text
    soup = BeautifulSoup(raw_html, "html.parser")

    # Remove non-content tags
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()

    # Get visible text content
    cleaned_text = soup.get_text(separator="\n", strip=True)

    # Limit to 12000 chars to avoid LLM token overflow
    cleaned_text = cleaned_text[:12000]

    logger.info(f"Scraped {len(cleaned_text)} chars from {url}")

    return {
        "raw_html": raw_html[:200000],  # store up to 200k chars
        "cleaned_text": cleaned_text,
    }


def extract_recipe_from_jsonld(raw_html: str, url: str) -> Optional[dict]:
    """
    Best-effort recipe extraction from JSON-LD (schema.org/Recipe).
    This is useful when LLM quota is exceeded or a site blocks AI extraction.
    """
    if not raw_html:
        return None

    soup = BeautifulSoup(raw_html, "html.parser")
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    if not scripts:
        return None

    def _as_list(x: Any) -> list:
        if x is None:
            return []
        return x if isinstance(x, list) else [x]

    def _is_recipe_type(t: Any) -> bool:
        if isinstance(t, str):
            return t.lower() == "recipe"
        if isinstance(t, list):
            return any(isinstance(i, str) and i.lower() == "recipe" for i in t)
        return False

    candidates: list[dict] = []
    for s in scripts:
        text = (s.string or s.get_text() or "").strip()
        if not text:
            continue
        try:
            data = json.loads(text)
        except Exception:
            continue

        for node in _as_list(data):
            if isinstance(node, dict) and _is_recipe_type(node.get("@type")):
                candidates.append(node)
            # Many sites embed within @graph
            if isinstance(node, dict) and isinstance(node.get("@graph"), list):
                for g in node["@graph"]:
                    if isinstance(g, dict) and _is_recipe_type(g.get("@type")):
                        candidates.append(g)

    if not candidates:
        return None

    recipe = candidates[0]
    title = recipe.get("name") or recipe.get("headline") or None
    if not title:
        return None

    # Ingredients are usually a list of strings
    ingredients = []
    for ing in _as_list(recipe.get("recipeIngredient")):
        if isinstance(ing, str) and ing.strip():
            ingredients.append({"quantity": None, "unit": None, "item": ing.strip()})

    # Instructions can be strings, HowToStep dicts, or HowToSection
    instructions_raw = recipe.get("recipeInstructions")
    steps: list[str] = []
    for inst in _as_list(instructions_raw):
        if isinstance(inst, str) and inst.strip():
            steps.append(inst.strip())
        elif isinstance(inst, dict):
            if isinstance(inst.get("text"), str) and inst["text"].strip():
                steps.append(inst["text"].strip())
            elif isinstance(inst.get("itemListElement"), list):
                for el in inst["itemListElement"]:
                    if isinstance(el, dict) and isinstance(el.get("text"), str) and el["text"].strip():
                        steps.append(el["text"].strip())

    instructions = [
        {"step_number": i + 1, "instruction_text": s}
        for i, s in enumerate(steps)
        if s
    ]

    def _duration_str(v: Any) -> Optional[str]:
        if isinstance(v, str) and v.strip():
            return v.strip()
        return None

    cuisine = None
    rc = recipe.get("recipeCuisine")
    if isinstance(rc, str):
        cuisine = rc
    elif isinstance(rc, list) and rc and isinstance(rc[0], str):
        cuisine = rc[0]

    servings = recipe.get("recipeYield")
    if isinstance(servings, list):
        servings = servings[0] if servings else None
    if servings is not None and not isinstance(servings, str):
        servings = str(servings)

    return {
        "title": title,
        "cuisine": cuisine,
        "difficulty": None,
        "prep_time": _duration_str(recipe.get("prepTime")),
        "cook_time": _duration_str(recipe.get("cookTime")),
        "total_time": _duration_str(recipe.get("totalTime")),
        "servings": servings,
        "ingredients": ingredients,
        "instructions": instructions,
        "nutrition": None,
        "substitutions": [],
        "shopping_list": [],
        "related_recipes": [],
        "_extraction_method": "jsonld",
        "source_url": url,
    }
