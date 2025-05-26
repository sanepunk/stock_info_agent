import os
import requests
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Your Marketstack API key
API_KEY = os.getenv("MARKETSTACK_API_KEY")

def get_price(symbol: str) -> float:
    """
    Fetches the latest end-of-day (EOD) closing price for the given symbol.
    Uses the /v1/eod/latest endpoint from Marketstack.
    Raises ValueError if no data is found.
    """
    url = "https://api.marketstack.com/v1/eod/latest"
    params = {
        'access_key': API_KEY,
        'symbols': symbol
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        # Ensure data list exists and is non-empty
        if 'data' in data and data['data']:
            return float(data['data'][0]['close'])
        else:
            raise ValueError(f"No data found for symbol: {symbol}")
    except requests.exceptions.HTTPError as http_err:
        raise SystemExit(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        raise SystemExit(f"Request exception: {req_err}")
    except ValueError as val_err:
        raise SystemExit(f"Value error: {val_err}")