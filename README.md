# RecipeMind AI

> An intelligent, full-stack recipe extraction and meal planning platform powered by **Google Gemini** (via LangChain), **FastAPI**, **PostgreSQL**, and **React**.

## Live Links

- **Frontend (Vercel)**: `https://recipe-mind-h2dxtltoe-prabhav-rathis-projects.vercel.app/`
- **Backend API (Render)**: `https://recipemind-backend.onrender.com/`
- **Demo Video**: `https://drive.google.com/file/d/1a9ssFaDkckUmrxa1Qs0iq-FsSbxpKzEQ/view?usp=sharing`

---

## Features

- **Intelligent Web Scraping:** Extracts structured content from any recipe blog URL using BeautifulSoup (No external recipe APIs required).
- **AI-Powered Parsing:** Uses Google Gemini (v2.5 Flash) to analyze raw HTML and extract ingredients, instructions, and metadata.
- **Nutritional Estimation & Substitutions:** Automatically generates calorie estimates and healthy ingredient substitutions.
- **Categorized Shopping Lists:** Breaks down ingredients by supermarket aisle (Produce, Dairy, Pantry, etc.).
- **Meal Planner:** Select multiple saved recipes to instantly generate a deduplicated, combined master shopping list.
- **Instant Caching:** Previously extracted URLs load instantly from the PostgreSQL database.
- **Clean UI/UX:** A responsive, accessible React frontend with a classic, clean design.

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend API** | FastAPI (Python 3.11+) |
| **Database** | PostgreSQL 16 & SQLAlchemy |
| **Scraping Engine** | BeautifulSoup4 & lxml |
| **LLM Orchestration** | LangChain & Google Gemini 2.5 Flash |
| **Frontend UI** | React 18, Vite, TypeScript |
| **Styling** | Vanilla CSS |

---

## Project Structure

```text
RecipeMind_AI/
├── backend/
│   ├── main.py          # FastAPI application & REST endpoints
│   ├── database.py      # SQLAlchemy engine configuration
│   ├── models.py        # Relational database models
│   ├── schemas.py       # Pydantic validation schemas
│   ├── scraper.py       # Web scraping logic
│   ├── llm.py           # LangChain prompt execution
│   ├── crud.py          # PostgreSQL interactions
│   └── .env.example     # Environment variable template
├── frontend/
│   ├── src/             # React component architecture
│   └── vite.config.ts   # Build configuration
├── prompts/             # LangChain system instructions
└── sample_data/         # Test URLs and reference outputs
```

---

## Local Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 16
- [Google Gemini API Key](https://aistudio.google.com) (Free Tier)

### 1. Database Initialization
Open pgAdmin or your PostgreSQL CLI and create a blank database:
```sql
CREATE DATABASE recipemind;
```

### 2. Backend Setup
```bash
cd backend

# Create and activate a Python virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # Mac/Linux

# Install required dependencies
pip install -r requirements.txt

# Configure your environment variables
copy .env.example .env
# Edit .env and insert your GEMINI_API_KEY and PostgreSQL DB password.

# Launch the FastAPI server (Tables will auto-generate on startup)
uvicorn main:app --reload --port 8000
```
> **Backend API:** `http://localhost:8000`  
> **Interactive Docs:** `http://localhost:8000/docs`

### 3. Frontend Setup
Open a **new terminal tab**:
```bash
cd frontend
npm install
npm run dev
```
> **Frontend App:** `http://localhost:5173`

---

## Core API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/extract` | Scrapes URL and returns AI-structured recipe data. |
| `GET`  | `/api/recipes` | Retrieves paginated history of saved recipes. |
| `GET`  | `/api/recipes/{id}` | Fetches detailed data for a specific recipe. |
| `DELETE`| `/api/recipes/{id}` | Removes a recipe from the database. |
| `POST` | `/api/meal-plan` | Combines ingredients from multiple recipes into one list. |

---

## Sample URLs for Testing

Test the extraction engine with these robust recipe links:
1. `https://www.allrecipes.com/recipe/23891/grilled-cheese-sandwich/`
2. `https://www.allrecipes.com/recipe/10813/best-chocolate-chip-cookies/`
3. `https://www.simplyrecipes.com/recipes/spaghetti_carbonara/`

---
*Built for advanced AI web development.*
