import os
import json
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from jinja2 import Environment, FileSystemLoader

# Paths resolved relative to this file so they work from any working directory
TEMPLATES_DIR = Path(__file__).parents[3] / "knowledge" / "templates"
OUTPUT_DIR = Path("output/demos")

CATEGORY_MAP = {
    "restaurant": "restaurant.html",
    "cafe": "restaurant.html",
    "coffee": "restaurant.html",
    "food": "restaurant.html",
    "bar": "restaurant.html",
    "bistro": "restaurant.html",
    "spa": "spa.html",
    "massage": "spa.html",
    "wellness": "spa.html",
    "beauty": "spa.html",
    "salon": "spa.html",
    "fitness": "fitness.html",
    "gym": "fitness.html",
    "sport": "fitness.html",
    "yoga": "fitness.html",
    "muay thai": "fitness.html",
}


class WebsiteGeneratorInput(BaseModel):
    business_name: str = Field(description="Full name of the business")
    category: str = Field(description="Business category (restaurant, spa, fitness, etc.)")
    address: str = Field(description="Full business address")
    phone: str = Field(description="Business phone number")
    description: str = Field(default="", description="Short business description or tagline")
    rating: float = Field(default=0.0, description="Google Maps star rating")
    reviews_count: int = Field(default=0, description="Total number of Google reviews")


class WebsiteGeneratorTool(BaseTool):
    name: str = "Demo Website Generator"
    description: str = (
        "Generates a personalized HTML landing page for a local business and saves it. "
        "Required: business_name, category, address, phone. "
        "Optional: description, rating, reviews_count. "
        "Returns a JSON with filepath, filename, and template_used."
    )
    args_schema: Type[BaseModel] = WebsiteGeneratorInput

    def _run(
        self,
        business_name: str,
        category: str,
        address: str,
        phone: str,
        description: str = "",
        rating: float = 0.0,
        reviews_count: int = 0,
    ) -> str:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        cat_lower = category.lower()
        template_file = "general.html"
        for keyword, tmpl in CATEGORY_MAP.items():
            if keyword in cat_lower:
                template_file = tmpl
                break

        try:
            env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
            template = env.get_template(template_file)
        except Exception as e:
            return f"ERROR: Could not load template '{template_file}' — {str(e)}"

        html = template.render(
            business_name=business_name,
            category=category,
            address=address,
            phone=phone,
            description=description,
            rating=rating or "",
            reviews_count=reviews_count or "",
        )

        slug = (
            business_name.lower()
            .replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")[:50]
        )
        filename = f"{slug}.html"
        filepath = OUTPUT_DIR / filename

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        return json.dumps({
            "filepath": str(filepath),
            "filename": filename,
            "template_used": template_file,
            "status": "generated",
        })
