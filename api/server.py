import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

from services.serper_client import SerperClient
from scraping.recipe_scraper import RecipeScraper
from services.nutrition_client import NutritionClient
from models.recipe_models import RecipeNutritionReport

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Recipe & Nutrition Helper",
    description="Search recipes, scrape data, and analyze nutrition",
    version="1.0.0",
)


class AnalyzeRequest(BaseModel):
    """Request body for POST /analyze endpoint."""
    ingredient: str
    preference: Optional[str] = None
    max_results: int = 4


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/analyze-simple")
def analyze_simple(
    ingredient: str,
    preference: Optional[str] = None,
    top_n: int = 4,
):
    """
    Simple GET endpoint for recipe + nutrition analysis.
    
    Args:
        ingredient: Ingredient/dish to search for (e.g., "paneer")
        preference: Optional preference (e.g., "healthy", "quick")
        top_n: Number of search results to consider (default: 4)
    
    Returns:
        Recipe + nutrition report
    """
    return analyze_recipe(ingredient, preference, top_n)


@app.post("/analyze")
def analyze_recipe_endpoint(request: AnalyzeRequest):
    """
    POST endpoint for recipe + nutrition analysis.
    
    Args:
        request: AnalyzeRequest with ingredient, preference, max_results
    
    Returns:
        Recipe + nutrition report
    """
    return analyze_recipe(request.ingredient, request.preference, request.max_results)


def analyze_recipe(ingredient: str, preference: Optional[str] = None, max_results: int = 4):
    """
    Core analysis pipeline: Search → Scrape → Nutrition.
    
    Args:
        ingredient: Ingredient/dish to search
        preference: Optional preference filter
        max_results: Number of URLs to try scraping
    
    Returns:
        RecipeNutritionReport as dict
    """
    try:
        # Build search query
        search_query = ingredient
        if preference:
            search_query += f" {preference}"
        
        # Step 1: Serper search
        serper = SerperClient()
        urls = serper.get_top_urls(search_query, count=max_results)
        
        if not urls:
            raise HTTPException(status_code=404, detail=f"No recipes found for '{search_query}'")
        
        # Step 2: Scrape first valid recipe
        recipe = RecipeScraper.scrape_first_valid_recipe(urls)
        
        if not recipe:
            raise HTTPException(status_code=404, detail=f"Could not extract recipe from search results")
        
        # Step 3: Analyze nutrition
        nutrition_client = NutritionClient()
        nutrition = nutrition_client.analyze_ingredients(recipe.ingredients)
        
        # Build report
        report = RecipeNutritionReport(
            recipe=recipe,
            nutrition=nutrition,
            search_query=ingredient,
            preference=preference,
        )
        
        return report.to_dict()
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/docs")
def docs():
    """Redirect to Swagger UI documentation."""
    return {"message": "Visit /docs for Swagger UI or /redoc for ReDoc"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
