import os
from dotenv import load_dotenv

load_dotenv()


def get_api_key(key_name: str) -> str:
    value = os.getenv(key_name)
    if not value:
        raise EnvironmentError(
            f"Missing required environment variable: '{key_name}'. "
            f"Add it to your .env file. See .env.example for reference."
        )
    return value


def format_large_number(value) -> str:
    if value is None or value != value:
        return "N/A"
    try:
        value = float(value)
        if value >= 1_000_000_000_000:
            return f"${value / 1_000_000_000_000:.2f}T"
        elif value >= 1_000_000_000:
            return f"${value / 1_000_000_000:.2f}B"
        elif value >= 1_000_000:
            return f"${value / 1_000_000:.2f}M"
        else:
            return f"${value:,.0f}"
    except (TypeError, ValueError):
        return "N/A"


def safe_round(value, decimals: int = 2) -> str:
    if value is None or value != value:
        return "N/A"
    try:
        return str(round(float(value), decimals))
    except (TypeError, ValueError):
        return "N/A"


def get_ticker_for_company(company_name: str) -> str:
    ticker_map = {
        # Indian IT
        "infosys": "INFY.NS",
        "tcs": "TCS.NS",
        "tata consultancy": "TCS.NS",
        "tata consultancy services": "TCS.NS",
        "wipro": "WIPRO.NS",
        "hcl": "HCLTECH.NS",
        "hcl technologies": "HCLTECH.NS",
        "tech mahindra": "TECHM.NS",
        # Indian consumer
        "zomato": "ZOMATO.NS",
        "swiggy": "SWIGGY.NS",
        # Indian banking
        "hdfc bank": "HDFCBANK.NS",
        "icici bank": "ICICIBANK.NS",
        "sbi": "SBIN.NS",
        "state bank": "SBIN.NS",
        "state bank of india": "SBIN.NS",
        "axis bank": "AXISBANK.NS",
        "kotak": "KOTAKBANK.NS",
        "kotak mahindra": "KOTAKBANK.NS",
        # Indian conglomerates
        "reliance": "RELIANCE.NS",
        "reliance industries": "RELIANCE.NS",
        "tata motors": "TATAMOTORS.NS",
        "bajaj finance": "BAJFINANCE.NS",
        "adani enterprises": "ADANIENT.NS",
        "adani ports": "ADANIPORTS.NS",
        "maruti": "MARUTI.NS",
        "maruti suzuki": "MARUTI.NS",
        "asian paints": "ASIANPAINT.NS",
        "sun pharma": "SUNPHARMA.NS",
        "sun pharmaceutical": "SUNPHARMA.NS",
        # US Tech
        "apple": "AAPL",
        "microsoft": "MSFT",
        "google": "GOOGL",
        "alphabet": "GOOGL",
        "amazon": "AMZN",
        "meta": "META",
        "netflix": "NFLX",
        "nvidia": "NVDA",
        "tesla": "TSLA",
    }
    normalized = company_name.strip().lower()
    return ticker_map.get(normalized, company_name.upper())
