from utils.price_change import get_price_change
from utils.get_news import get_news

def analyze(symbol: str, days: int = 1) -> dict:
    """
    Summarizes recent price movement:
      - Calculates % change over `days`
      - Picks top news headline
      - Returns dict with symbol, change_pct, sentiment, and headline
    """
    change_pct = get_price_change(symbol, days)
    articles = get_news(symbol, limit=3)
    sentiment = "up" if change_pct > 0 else "down"
    headline = articles[0]["title"] if articles else "no major news"
    return {
        "symbol": symbol,
        "change_pct": round(change_pct, 2),
        "sentiment": sentiment,
        "top_headline": headline
    }