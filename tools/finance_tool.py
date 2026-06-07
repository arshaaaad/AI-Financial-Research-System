import json
from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from langchain.tools import tool

from utils.helpers import format_large_number, get_ticker_for_company, safe_round


def build_stock_chart(ticker_symbol: str, history_df: pd.DataFrame) -> go.Figure:
    """Build an interactive Plotly line chart with 20-day moving average."""
    df = history_df.copy()
    df["MA20"] = df["Close"].rolling(window=20).mean()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["Close"],
        mode="lines",
        name="Close Price",
        line=dict(color="#2563EB", width=2),
        fill="tozeroy",
        fillcolor="rgba(37, 99, 235, 0.07)",
        hovertemplate="<b>%{x|%d %b %Y}</b><br>Price: %{y:.2f}<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["MA20"],
        mode="lines",
        name="20-Day MA",
        line=dict(color="#F59E0B", width=1.5, dash="dash"),
        hovertemplate="<b>%{x|%d %b %Y}</b><br>MA20: %{y:.2f}<extra></extra>",
    ))

    fig.update_layout(
        title=dict(
            text=f"<b>{ticker_symbol}</b> — 6-Month Price History",
            font=dict(size=16, family="Inter, sans-serif"),
        ),
        xaxis=dict(
            title="Date",
            showgrid=True,
            gridcolor="rgba(200,200,200,0.15)",
            tickformat="%b %Y",
        ),
        yaxis=dict(
            title="Price",
            showgrid=True,
            gridcolor="rgba(200,200,200,0.15)",
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=60, b=20),
        height=400,
        font=dict(family="Inter, sans-serif"),
    )

    return fig


def build_comparison_chart(
    ticker_a: str,
    history_a: pd.DataFrame,
    ticker_b: str,
    history_b: pd.DataFrame,
) -> go.Figure:
    """Build a normalised price comparison chart for two tickers (base = 100)."""
    fig = go.Figure()

    for ticker, df, color in [
        (ticker_a, history_a, "#2563EB"),
        (ticker_b, history_b, "#10B981"),
    ]:
        df = df.copy()
        base = df["Close"].iloc[0]
        df["Normalised"] = (df["Close"] / base) * 100

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["Normalised"],
            mode="lines",
            name=ticker,
            line=dict(color=color, width=2),
            hovertemplate=f"<b>{ticker}</b><br>%{{x|%d %b %Y}}<br>Index: %{{y:.1f}}<extra></extra>",
        ))

    fig.update_layout(
        title=dict(
            text=f"<b>{ticker_a} vs {ticker_b}</b> — Normalised 6-Month Return (Base = 100)",
            font=dict(size=15, family="Inter, sans-serif"),
        ),
        xaxis=dict(title="Date", showgrid=True, gridcolor="rgba(200,200,200,0.15)", tickformat="%b %Y"),
        yaxis=dict(title="Indexed Price (Base = 100)", showgrid=True, gridcolor="rgba(200,200,200,0.15)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=70, b=20),
        height=400,
        font=dict(family="Inter, sans-serif"),
    )

    return fig


@tool
def get_financial_data(company_name: str) -> str:
    """
    Fetch key financial metrics and 6-month stock price history for a company
    using Yahoo Finance. Accepts a company name (e.g. 'Infosys') or ticker symbol.
    Returns a JSON string with price, market cap, P/E ratio, revenue, and history.
    """
    ticker_symbol = get_ticker_for_company(company_name)

    result = {
        "ticker": ticker_symbol,
        "company_name": company_name,
        "current_price": "N/A",
        "market_cap": "N/A",
        "pe_ratio": "N/A",
        "revenue": "N/A",
        "currency": "N/A",
        "52_week_high": "N/A",
        "52_week_low": "N/A",
        "dividend_yield": "N/A",
        "history_available": False,
    }

    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info

        if not info or info.get("regularMarketPrice") is None:
            result["error"] = (
                f"Could not retrieve data for '{ticker_symbol}'. "
                "The ticker may be incorrect or unavailable."
            )
            return json.dumps(result)

        result["current_price"] = safe_round(
            info.get("currentPrice") or info.get("regularMarketPrice"), 2
        )
        result["market_cap"] = format_large_number(info.get("marketCap"))
        result["pe_ratio"] = safe_round(info.get("trailingPE"), 2)
        result["revenue"] = format_large_number(info.get("totalRevenue"))
        result["currency"] = info.get("currency", "N/A")
        result["52_week_high"] = safe_round(info.get("fiftyTwoWeekHigh"), 2)
        result["52_week_low"] = safe_round(info.get("fiftyTwoWeekLow"), 2)
        result["beta"] = safe_round(info.get("beta"), 2)
        result["eps"] = safe_round(info.get("trailingEps"), 2)
        result["profit_margin"] = (
            f"{round(info.get('profitMargins', 0) * 100, 2)}%"
            if info.get("profitMargins") else "N/A"
        )
        result["debt_to_equity"] = safe_round(info.get("debtToEquity"), 2)
        result["roe"] = (
            f"{round(info.get('returnOnEquity', 0) * 100, 2)}%"
            if info.get("returnOnEquity") else "N/A"
        )

        div_yield = info.get("dividendYield")
        result["dividend_yield"] = (
            f"{round(div_yield * 100, 2)}%" if div_yield else "N/A"
        )

        end_date = datetime.today()
        start_date = end_date - timedelta(days=182)
        history = ticker.history(
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
        )

        if not history.empty and "Close" in history.columns:
            result["history_available"] = True
            result["6m_high"] = safe_round(history["Close"].max(), 2)
            result["6m_low"] = safe_round(history["Close"].min(), 2)
            result["6m_return_pct"] = safe_round(
                (history["Close"].iloc[-1] - history["Close"].iloc[0])
                / history["Close"].iloc[0] * 100,
                2,
            )

            history_slim = history["Close"].tail(130).reset_index()
            history_slim.columns = ["Date", "Close"]
            history_slim["Date"] = history_slim["Date"].astype(str)
            result["history_data"] = history_slim.to_dict(orient="records")

    except Exception as exc:
        result["error"] = f"Unexpected error: {str(exc)}"

    return json.dumps(result)
