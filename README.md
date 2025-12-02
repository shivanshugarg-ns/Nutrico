# Recipe & Nutrition Helper

A FastAPI-based application that searches for recipes, scrapes recipe data, and analyzes nutrition information.

## What It Does

1. **Web Search** → Uses Serper API to search for recipes
2. **Data Scraping** → Extracts recipe data (ingredients, steps) from the top 4 results using JSON-LD
3. **Nutrition Analysis** → Calls API Ninjas to compute nutrition values for ingredients
4. **REST API** → Exposes all functionality through FastAPI endpoints

## Tech Stack

- **Python 3.10+**
- **FastAPI** — REST API framework
- **Uvicorn** — ASGI web server
- **requests** — HTTP client library
- **beautifulsoup4** — HTML parsing
- **python-dotenv** — Environment variable management

## Folder Structure

```
recipe_nutri_helper/
├── api/
│   ├── __init__.py
│   └── server.py            ← FastAPI server & endpoints
├── services/
│   ├── __init__.py
│   ├── serper_client.py     ← Serper API integration
│   └── nutrition_client.py  ← Nutrition API integration
├── scraping/
│   ├── __init__.py
│   └── recipe_scraper.py    ← JSON-LD recipe extraction
├── models/
│   ├── __init__.py
│   └── recipe_models.py     ← Recipe & Nutrition dataclasses
├── utils/
│   ├── __init__.py
│   └── http_client.py       ← HTTP client with retry logic
├── logs/
│   └── .gitkeep
├── postman_collection.json
├── requirements.txt
├── README.md
├── .env
├── .env.example
└── .gitignore
```

## Setup

### 1. Create Virtual Environment

```bash
cd recipe_nutri_helper
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```
SERPER_API_KEY=your_serper_key_here
NINJA_API_KEY=your_api_ninjas_key_here
```

**Get API Keys:**
- **Serper API**: https://serper.dev (free tier available)
- **API Ninjas**: https://api-ninjas.com/register (free tier: 50 requests/month)

## How It Works

### HTTP Client with Retry (`utils/http_client.py`)

All network requests go through `HTTPClient` which:
- Attempts the request once
- Automatically retries once if it fails
- Raises `HTTPError` if both attempts fail

Methods:
- `get(url, headers)` — GET request
- `post(url, data, headers)` — POST request
- `fetch_html(url)` — Fetch raw HTML

### Serper API (`services/serper_client.py`)

Integrates with Serper's Google search API:

```python
serper = SerperClient(api_key="your_key")
urls = serper.get_top_urls("paneer healthy recipe", count=4)
# Returns: ['url1', 'url2', 'url3', 'url4']
```

**Endpoint:** `POST https://google.serper.dev/search`

**Header:** `X-API-KEY: your_key`

### Recipe Scraper (`scraping/recipe_scraper.py`)

Extracts recipe data from websites using JSON-LD:

```python
recipe = RecipeScraper.scrape_recipe("https://example.com/recipe")
# Returns: Recipe(title, ingredients, steps, servings, source_url)
```

**Process:**
1. Fetches HTML from URL (with retry)
2. Parses HTML with BeautifulSoup
3. Finds all `<script type="application/ld+json">` tags
4. Extracts first object with `"@type": "Recipe"`
5. Parses ingredients, steps, servings, title

**Key Methods:**
- `scrape_recipe(url)` — Scrape single URL
- `scrape_first_valid_recipe(urls)` — Try multiple URLs, return first valid recipe

**Tries up to 4 URLs and stops after first valid recipe.**

### Nutrition API (`services/nutrition_client.py`)

Uses API Ninjas Nutrition API (free fields only):

```python
nutrition = NutritionClient(api_key="your_key")
data = nutrition.get_nutrition("paneer")
# Returns: NutritionData with aggregated free fields
```

**Free Fields Returned:**
- `serving_size_g`
- `fat_total_g`
- `fat_saturated_g`
- `carbohydrates_total_g`
- `fiber_g`
- `sugar_g`
- `sodium_mg`
- `potassium_mg`
- `cholesterol_mg`

**Note:** Premium fields (calories, protein_g, etc.) are ignored.

**Endpoint:** `GET https://api.api-ninjas.com/v1/nutrition?query=<ingredient>`

**Header:** `X-Api-Key: your_key`

## FastAPI Server (`api/server.py`)

### Endpoints

#### 1. GET /health
Health check endpoint.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{"status": "ok"}
```

#### 2. POST /analyze
Full recipe + nutrition analysis.

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "ingredient": "paneer",
    "preference": "healthy",
    "max_results": 4
  }'
```

**Request:**
```json
{
  "ingredient": "paneer",
  "preference": "healthy",
  "max_results": 4
}
```

**Response:**
```json
{
  "recipe": {
    "title": "Paneer Tikka",
    "ingredients": [
      {"name": "paneer", "amount": "200", "unit": "g"},
      {"name": "yogurt", "amount": "100", "unit": "ml"}
    ],
    "steps": [
      {"text": "Marinate paneer...", "order": 0},
      {"text": "Grill at 200°C...", "order": 1}
    ],
    "servings": 2,
    "source_url": "https://example.com/recipe"
  },
  "nutrition": {
    "serving_size_g": 300.0,
    "fat_total_g": 10.5,
    "fat_saturated_g": 6.2,
    "carbohydrates_total_g": 5.0,
    "fiber_g": 0.0,
    "sugar_g": 2.1,
    "sodium_mg": 450.0,
    "potassium_mg": 180.0,
    "cholesterol_mg": 25.0
  },
  "search_query": "paneer",
  "preference": "healthy"
}
```

#### 3. GET /analyze-simple
Same as POST /analyze but using query parameters.

```bash
curl "http://localhost:8000/analyze-simple?ingredient=paneer&preference=healthy&top_n=4"
```

**Query Parameters:**
- `ingredient` (required): Ingredient/dish name
- `preference` (optional): Preference filter (e.g., "healthy", "quick", "vegetarian")
- `top_n` (optional, default: 4): Number of search results to try

## Running the Server

```bash
uvicorn api.server:app --reload --port 8000
```

The server runs on `http://localhost:8000`

**Swagger UI (Interactive docs):** http://localhost:8000/docs
**ReDoc (Alternative docs):** http://localhost:8000/redoc

## Error Handling & Retry Logic

- **HTTP Failures:** All network calls retry once (GET, POST, HTML fetch)
- **Invalid Recipes:** Tries up to 4 search results; returns error if none valid
- **API Key Missing:** Raises `ValueError` at startup
- **Nutrition API Errors:** Returns empty NutritionData if call fails
- **Serper API Errors:** Returns empty results list if call fails

**Custom Exceptions:**
- `HTTPError` — Network call failed after retry

## Testing with Postman

1. **Import Collection:**
   - Open Postman
   - Click "Import" → Select `postman_collection.json`

2. **Set Up Environment Variables (Optional):**
   - Create a Postman environment variable `base_url` = `http://127.0.0.1:8000`

3. **Test Requests:**
   - Click "GET /health" → Send
   - Click "POST /analyze" → Send
   - Click "GET /analyze-simple" → Send

All 3 requests are pre-configured in the collection.

## Git Workflow

This project uses a clean Git feature-branch workflow:

### Initial Setup
```bash
git init
git add .gitignore requirements.txt README.md
git commit -m "chore: initial setup"
git remote add origin https://github.com/shivanshugarg-ns/recipe_nutri_helper.git
git branch -M main
git push -u origin main
```

### Feature Branches

**1. feature/serper-api**
```bash
git checkout -b feature/serper-api
git add services/serper_client.py
git commit -m "feat: Serper API search integration"
git push -u origin feature/serper-api
```

**2. feature/scraper**
```bash
git checkout -b feature/scraper
git add scraping/recipe_scraper.py
git commit -m "feat: JSON-LD recipe scraper"
git push -u origin feature/scraper
```

**3. feature/nutrition**
```bash
git checkout -b feature/nutrition
git add services/nutrition_client.py
git commit -m "feat: nutrition analysis (free fields)"
git push -u origin feature/nutrition
```

**4. feature/api-server**
```bash
git checkout -b feature/api-server
git add api/server.py
git commit -m "feat: FastAPI server + endpoints"
git push -u origin feature/api-server
```

**5. feature/docs**
```bash
git checkout -b feature/docs
git add README.md postman_collection.json .env.example
git commit -m "docs: Postman collection, README, env example"
git push -u origin feature/docs
```

### Merging to Main
After testing, merge each feature branch via pull requests (or direct merge):

```bash
git checkout main
git merge feature/serper-api
git push origin main
```

## Requirements Mapping

| Requirement | File | Details |
|---|---|---|
| Scrape public website | `scraping/recipe_scraper.py` | Extracts JSON-LD from recipe websites |
| Use Serper API | `services/serper_client.py` | Google search integration |
| Use 1 scenario API | `services/nutrition_client.py` | API Ninjas nutrition lookup |
| Error handling + retry | `utils/http_client.py` | Automatic 1 retry on all network calls |
| FastAPI server | `api/server.py` | 3 endpoints: /health, /analyze, /analyze-simple |
| Git with feature branches | Multiple commits | 5 feature branches as documented |
| Postman collection | `postman_collection.json` | 3 pre-configured requests |
| Complete README | `README.md` | This file |
| Clean repo structure | Folder layout | Organized by functionality |

## Next Steps

1. Set up API keys (Serper + API Ninjas)
2. Run `pip install -r requirements.txt`
3. Configure `.env` file
4. Start server: `uvicorn api.server:app --reload --port 8000`
5. Test with Postman or curl
6. Push feature branches to GitHub

## License

MIT
