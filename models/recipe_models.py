from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any


@dataclass
class Ingredient:
    """Represents a recipe ingredient."""
    name: str
    amount: Optional[str] = None
    unit: Optional[str] = None


@dataclass
class RecipeStep:
    """Represents a recipe step."""
    text: str
    order: Optional[int] = None


@dataclass
class Recipe:
    """Represents a complete recipe with metadata."""
    title: str
    ingredients: List[Ingredient] = field(default_factory=list)
    steps: List[RecipeStep] = field(default_factory=list)
    servings: Optional[int] = None
    source_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "ingredients": [{"name": ing.name, "amount": ing.amount, "unit": ing.unit} for ing in self.ingredients],
            "steps": [{"text": step.text, "order": step.order} for step in self.steps],
            "servings": self.servings,
            "source_url": self.source_url,
        }


@dataclass
class NutritionData:
    """Represents nutrition information (free fields only from API Ninjas)."""
    serving_size_g: float = 0.0
    fat_total_g: float = 0.0
    fat_saturated_g: float = 0.0
    carbohydrates_total_g: float = 0.0
    fiber_g: float = 0.0
    sugar_g: float = 0.0
    sodium_mg: float = 0.0
    potassium_mg: float = 0.0
    cholesterol_mg: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class RecipeNutritionReport:
    """Combined recipe + nutrition analysis."""
    recipe: Recipe
    nutrition: NutritionData
    search_query: str
    preference: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "recipe": self.recipe.to_dict(),
            "nutrition": self.nutrition.to_dict(),
            "search_query": self.search_query,
            "preference": self.preference,
        }
