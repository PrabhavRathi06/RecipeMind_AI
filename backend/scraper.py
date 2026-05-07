import requests
from bs4 import BeautifulSoup
import logging

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
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
    except requests.exceptions.MissingSchema:
        raise ValueError(f"Invalid URL format: {url}")
    except requests.exceptions.ConnectionError:
        raise ValueError(f"Could not connect to: {url}")
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
