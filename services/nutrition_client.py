import os
from typing import List
from utils.http_client import HTTPClient
from models.recipe_models import NutritionData, Ingredient


class NutritionClient:
    """Client for API Ninjas Nutrition API (free fields only)."""
    
    BASE_URL = "https://api.api-ninjas.com/v1/nutrition"
    
    # Free fields returned by API Ninjas
    FREE_FIELDS = [
        "serving_size_g",
        "fat_total_g",
        "fat_saturated_g",
        "carbohydrates_total_g",
        "fiber_g",
        "sugar_g",
        "sodium_mg",
        "potassium_mg",
        "cholesterol_mg",
    ]
    
    def __init__(self, api_key: str = None):
        """
        Initialize Nutrition client.
        
        Args:
            api_key: API Ninjas API key. If None, reads from NINJA_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("NINJA_API_KEY")
        if not self.api_key:
            raise ValueError("NINJA_API_KEY not found in environment or arguments")
    
    def get_nutrition(self, query: str) -> NutritionData:
        """
        Get nutrition data for an ingredient/food query.
        
        Args:
            query: Food/ingredient name to analyze
            
        Returns:
            NutritionData object with aggregated free fields
        """
        headers = {
            "X-Api-Key": self.api_key,
        }
        
        params = {"query": query}
        
        try:
            # Build URL with query param
            url = f"{self.BASE_URL}?query={query}"
            response = HTTPClient.get(url, headers=headers)
            
            # Sum all free fields from all results
            aggregated = NutritionData()
            
            if isinstance(response, list):
                items = response
            else:
                items = [response] if response else []
            
            for item in items:
                if isinstance(item, dict):
                    for field in self.FREE_FIELDS:
                        value = item.get(field, 0)
                        if value and isinstance(value, (int, float)):
                            setattr(aggregated, field, getattr(aggregated, field) + float(value))
            
            return aggregated
        except Exception as e:
            print(f"Nutrition lookup failed for '{query}': {e}")
            return NutritionData()
    
    def analyze_ingredients(self, ingredients: List[Ingredient]) -> NutritionData:
        """
        Analyze all ingredients and aggregate nutrition data.
        
        Args:
            ingredients: List of Ingredient objects
            
        Returns:
            Aggregated NutritionData
        """
        aggregated = NutritionData()
        
        for ingredient in ingredients:
            nutrition = self.get_nutrition(ingredient.name)
            
            # Sum all fields
            for field in self.FREE_FIELDS:
                current = getattr(aggregated, field, 0)
                ingredient_value = getattr(nutrition, field, 0)
                setattr(aggregated, field, current + ingredient_value)
        
        return aggregated
