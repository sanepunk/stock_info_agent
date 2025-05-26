import os
import requests
NEWS_API_URL = os.getenv("NEWS_URL")      # Base URL for news API
NEWS_KEY = os.getenv("NEWS_API_KEY")      # Your News API key

def get_news(symbol: str, limit: int = 5) -> list:
    """
    Fetches the most recent `limit` news articles for a symbol.
    Uses NewsAPI's /v2/everything endpoint.
    Returns list of article dicts.
    """
    resp = requests.get(NEWS_API_URL, params={
        "q": symbol,
        "pageSize": limit,
        "sortBy": "publishedAt",
        "apiKey": NEWS_KEY
    }).json()
    return resp.get("articles", [])