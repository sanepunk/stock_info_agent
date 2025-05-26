import os           # For environment variable access
import re           # For regex-based text parsing
import requests     # For making HTTP requests
from dotenv import load_dotenv  # For loading .env files

# Load environment variables from a .env file
load_dotenv()

# --- AlphaVantage Configuration & Fallbacks ---
API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")  # Your Alpha Vantage API key
SEARCH_URL = "https://www.alphavantage.co/query"  # Base URL for Alpha Vantage queries

# Predefined mapping of common company names to ticker symbols
COMMON_TICKERS = {
    "google": "GOOGL",
    "alphabet": "GOOGL",
    "apple": "AAPL",
    "microsoft": "MSFT",
    "amazon": "AMZN",
    "facebook": "META",
    "meta": "META",
    "tesla": "TSLA",
    "nvidia": "NVDA",
    "palantir": "PLTR",
    # Add more mappings as needed
}

def identify_ticker(query: str) -> str:
    """
    Attempts to identify the ticker symbol from a user query.
    1. Tokenizes the query and checks common mappings.
    2. Falls back to Alpha Vantage SYMBOL_SEARCH API if needed.
    Raises ValueError if no match is found.
    """
    # Extract alphanumeric tokens up to length 10
    tokens = re.findall(r"\b[A-Za-z]{1,10}\b", query.lower())
    for token in tokens:
        # 1. Check predefined mapping first
        if token in COMMON_TICKERS:
            return COMMON_TICKERS[token]
        # 2. Query Alpha Vantage SYMBOL_SEARCH
        params = {
            "function": "SYMBOL_SEARCH",
            "keywords": token,
            "apikey": API_KEY,
        }
        response = requests.get(SEARCH_URL, params=params)
        if response.status_code != 200:
            continue  # Skip token if API fails
        data = response.json()
        best_matches = data.get("bestMatches", [])
        for match in best_matches:
            symbol = match.get("1. symbol", "")
            name = match.get("2. name", "").lower()
            # Return symbol if token in company name
            if token in name:
                return symbol
    # If none found, error out
    raise ValueError("Could not identify a ticker symbol in query.")