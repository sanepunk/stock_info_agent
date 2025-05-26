import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Your Marketstack API key
API_KEY = os.getenv("MARKETSTACK_API_KEY")

def get_price_change(symbol: str, days: int = 1) -> float:
    """
    Calculates percentage change from `days` ago to most recent close.
    Fetches up to `days + buffer` of historical EOD data, sorts by date,
    and computes (latest - past) / past * 100.
    Raises ValueError if insufficient data.
    """
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days + 5)  # buffer for weekends
    date_from = start_date.strftime('%Y-%m-%d')
    date_to = end_date.strftime('%Y-%m-%d')
    url = "https://api.marketstack.com/v1/eod"
    params = {
        'access_key': API_KEY,
        'symbols': symbol,
        'date_from': date_from,
        'date_to': date_to,
        'limit': 1000
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json().get('data', [])
        if len(data) < days + 1:
            raise ValueError(f"Not enough data to calculate a {days}-day price change for symbol: {symbol}")
        # Sort descending by date
        sorted_data = sorted(data, key=lambda x: x['date'], reverse=True)
        latest_close = sorted_data[0]['close']
        past_close = sorted_data[days]['close']
        return ((latest_close - past_close) / past_close) * 100
    except requests.exceptions.HTTPError as http_err:
        raise SystemExit(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        raise SystemExit(f"Request exception: {req_err}")
    except ValueError as val_err:
        raise SystemExit(f"Value error: {val_err}")