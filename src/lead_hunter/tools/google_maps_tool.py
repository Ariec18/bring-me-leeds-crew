import os
import json
import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type


class GoogleMapsSearchInput(BaseModel):
    query: str = Field(description="Business type to search for (e.g. 'restaurants', 'spas')")
    location: str = Field(description="City or area to search in (e.g. 'Koh Samui, Thailand')")
    limit: int = Field(default=20, description="Max number of results to return (max 20)")


class GoogleMapsSearchTool(BaseTool):
    name: str = "Google Maps Business Search"
    description: str = (
        "Searches Google Maps for businesses by type and location via Serper API. "
        "Input: query (business type), location (city/area), limit (max results). "
        "Returns JSON with name, address, phone, website, rating, reviews_count, category."
    )
    args_schema: Type[BaseModel] = GoogleMapsSearchInput

    def _run(self, query: str, location: str, limit: int = 20) -> str:
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            return "ERROR: SERPER_API_KEY not set in environment."

        url = "https://google.serper.dev/maps"
        payload = json.dumps({"q": f"{query} in {location}", "num": min(limit, 20)})
        headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}

        try:
            response = requests.post(url, headers=headers, data=payload, timeout=15)
            response.raise_for_status()
        except requests.RequestException as e:
            return f"ERROR: Serper API request failed — {str(e)}"

        places = response.json().get("places", [])

        leads = []
        for place in places:
            leads.append({
                "name": place.get("title", ""),
                "address": place.get("address", ""),
                "phone": place.get("phoneNumber", ""),
                "website": place.get("website", ""),
                "rating": place.get("rating", 0),
                "reviews_count": place.get("reviewsCount", 0),
                "category": place.get("category", ""),
                "google_maps_url": f"https://maps.google.com/?cid={place.get('cid', '')}",
                "latitude": place.get("latitude", ""),
                "longitude": place.get("longitude", ""),
            })

        return json.dumps(leads, indent=2, ensure_ascii=False)
