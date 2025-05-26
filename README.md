# Stock Info Agent

A modular multi-agent system for answering stock-related queries using Google's Agent Development Kit (ADK), AlphaVantage, Marketstack, and NewsAPI. It features structured tool use and schema-based LLM output for comparison.

## 📁 Project Structure

├── main.py # Main runner with agent definitions and logic
├── requirements.txt # Python dependencies
├── output.txt # Example output from running the tool
├── .env # API keys configuration (not committed)
├── .gitignore # Ignored files and folders
└── utils/ # Utility modules (sub-agents)
├── identify_ticker.py # Ticker symbol resolution from user query
├── ticker_price.py # Fetches current price of stock
├── ticker_price_change.py # Computes % change over time
├── ticker_news.py # Retrieves recent news headlines
└── ticker_analysis.py # Synthesizes news and change to explain movement

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/sanepunk/stock_info_agent.git
cd stock_info_agent
```

### 2. Set Up Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory with the following keys:

```env
# AlphaVantage API
ALPHAVANTAGE_API_KEY=your_alpha_vantage_key

# Marketstack API
MARKETSTACK_API_KEY=your_marketstack_key

# News API
NEWS_API_KEY=your_newsapi_key
NEWS_URL=https://newsapi.org/v2/everything
```

### 4. Run the Application

```bash
python main.py
```

The system will run two agents per query:

- One uses tools (API-backed).
- One uses pure LLM-based schema generation.

Sample queries include:

- "Why did Tesla stock drop today?"
- "What's happening with Palantir stock recently?"
- "How has Nvidia stock changed in the last 7 days?"

## 🛠 Features

### Ticker Resolution

Parses free-form company names or tickers and matches them using custom mappings or AlphaVantage's search endpoint.

### Price Retrieval

Uses Marketstack's EOD data to get the latest available price.

### Change Computation

Calculates % change over time windows (e.g., 1 day, 7 days) with historical data.

### News Extraction

Fetches recent news articles related to a given ticker.

### Change Explanation

Combines % change and top headline into a summary explanation.

### ADK Integration

Implements two LlmAgents via Google’s Agent Development Kit (ADK):

- One that actually calls tools and returns structured data.
- One that fabricates structured data using only the model and schema.

## 🧪 Example Use Cases

- Compare API-powered vs. hallucinated agent output.
- Debug and prototype stock-based applications using modular utilities.
- Explore ADK session management and tool calling with real-time data.

## 📦 Dependencies

- `google-generativeai`
- `google-adk`
- `requests`
- `python-dotenv`
- `pydantic`

Install via:

```bash
pip install -r requirements.txt
```

## 🧩 Extending the Project

- Add new data sources by editing the relevant `utils/` module.
- Add agent variations or experiment with different LLMs by modifying `main.py`.
- Deploy with FastAPI or Flask to create a web-accessible agent API.

## 📜 License

This repository is licensed under the Apache 2.0 License.

**Author:** sanepunk
