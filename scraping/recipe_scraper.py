import json
from typing import Optional, List
from bs4 import BeautifulSoup
from utils.http_client import HTTPClient
from models.recipe_models import Recipe, Ingredient, RecipeStep


class RecipeScraper:
    """Scrapes recipe data from URLs using JSON-LD extraction."""
    
    @staticmethod
    def scrape_recipe(url: str) -> Optional[Recipe]:
        """
        Scrape recipe from a URL by extracting JSON-LD structured data.
        
        Args:
            url: Target URL to scrape
            
        Returns:
            Recipe object if found, None otherwise
        """
        try:
            html = HTTPClient.fetch_html(url)
            soup = BeautifulSoup(html, "html.parser")
            
            # Find all JSON-LD script tags
            script_tags = soup.find_all("script", {"type": "application/ld+json"})
            
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    
                    # Check if this is a Recipe type
                    if isinstance(data, dict) and data.get("@type") == "Recipe":
                        return RecipeScraper._parse_recipe_json(data, url)
                    
                    # Handle @graph case where Recipe might be nested
                    if isinstance(data, dict) and "@graph" in data:
                        for item in data["@graph"]:
                            if isinstance(item, dict) and item.get("@type") == "Recipe":
                                return RecipeScraper._parse_recipe_json(item, url)
                except (json.JSONDecodeError, TypeError):
                    continue
            
            return None
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    @staticmethod
    def _parse_recipe_json(data: dict, url: str) -> Recipe:
        """
        Parse JSON-LD recipe data into Recipe object.
        
        Args:
            data: JSON-LD recipe data
            url: Source URL
            
        Returns:
            Recipe object
        """
        title = data.get("name", "Unknown Recipe")
        servings = data.get("recipeYield", None)
        
        # Parse servings if it's a list
        if isinstance(servings, list):
            servings = servings[0] if servings else None
        
        # Parse servings if it's a string with number
        if isinstance(servings, str):
            try:
                servings = int("".join(filter(str.isdigit, servings.split()[0])))
            except (ValueError, IndexError):
                servings = None
        
        # Parse ingredients
        ingredients = []
        ingredients_data = data.get("recipeIngredient", [])
        if isinstance(ingredients_data, list):
            for ing in ingredients_data:
                if isinstance(ing, str):
                    ingredients.append(Ingredient(name=ing))
                elif isinstance(ing, dict):
                    ingredients.append(
                        Ingredient(
                            name=ing.get("name", ""),
                            amount=ing.get("amount", None),
                            unit=ing.get("unitCode", None),
                        )
                    )
        
        # Parse steps
        steps = []
        instructions = data.get("recipeInstructions", [])
        
        if isinstance(instructions, list):
            for idx, instruction in enumerate(instructions):
                if isinstance(instruction, str):
                    steps.append(RecipeStep(text=instruction, order=idx))
                elif isinstance(instruction, dict):
                    # Handle HowToStep structure
                    text = instruction.get("text") or instruction.get("description", "")
                    order = instruction.get("position", idx)
                    if text:
                        steps.append(RecipeStep(text=text, order=order))
        elif isinstance(instructions, str):
            steps.append(RecipeStep(text=instructions, order=0))
        elif isinstance(instructions, dict):
            # Single step object
            text = instructions.get("text") or instructions.get("description", "")
            if text:
                steps.append(RecipeStep(text=text, order=0))
        
        return Recipe(
            title=title,
            ingredients=ingredients,
            steps=steps,
            servings=servings,
            source_url=url,
        )
    
    @staticmethod
    def scrape_first_valid_recipe(urls: List[str]) -> Optional[Recipe]:
        """
        Scrape the first valid recipe from a list of URLs.
        
        Args:
            urls: List of URLs to try (max 4)
            
        Returns:
            First valid Recipe found, or None if none found
        """
        for url in urls[:4]:  # Try max 4 URLs
            recipe = RecipeScraper.scrape_recipe(url)
            if recipe:
                return recipe
        
        return None
