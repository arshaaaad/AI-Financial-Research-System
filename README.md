## Live Demo
https://ai-financial-research-system-tdbvxizl4awyozeaekawcg.streamlit.app/

# AI Financial Research Multi-Agent System

A production-ready, multi-agent AI system that performs comprehensive financial research on any publicly listed company. The pipeline combines live web search, real-time market data, and LLM-driven analysis into a professional Streamlit dashboard with PDF export.

---

## Overview

The system orchestrates three specialised LangChain agents that run sequentially:

1. **News Research Agent** — searches the web for the latest company news using Tavily and summarises findings with Llama 3.3 70B via Groq.
2. **Financial Data Agent** — fetches live stock metrics from Yahoo Finance, generates an interactive Plotly price chart, and provides an LLM-written interpretation.
3. **Executive Report Agent** — synthesises the outputs of Agents 1 and 2 into a structured equity research report with a Buy / Hold / Sell recommendation.

---

## Features

- Real-time news research via Tavily Search API
- Live financial data: price, market cap, P/E, revenue, EPS, profit margin, ROE, debt/equity
- Interactive 6-month stock price chart with 20-day moving average
- GPT-quality executive reports powered by Groq's Llama 3.3 70B (free tier available)
- Company comparison mode: side-by-side metrics table and normalised price chart
- Financial metrics dashboard with 12 key ratios across 3 rows
- Export report as Markdown or styled PDF (with ReportLab cover page)
- Research history saved in Streamlit session state
- Streamlit Cloud ready — no extra server configuration needed

---

## Architecture

```
Streamlit UI (app.py)
       |
       |-- Agent 1: News Research
       |       |-- TavilySearchResults (web search)
       |       |-- Llama 3.3 70B via Groq (summarisation)
       |
       |-- Agent 2: Financial Data
       |       |-- yFinance custom @tool (live market data)
       |       |-- Plotly (price chart)
       |       |-- Llama 3.3 70B via Groq (interpretation)
       |
       |-- Agent 3: Executive Report
               |-- Llama 3.3 70B via Groq (report generation)
               |-- ReportLab (PDF export)
```

---

## Project Structure

```
ai-financial-research/
├── app.py                      Main Streamlit application
├── agents/
│   ├── news_agent.py           Agent 1: news research with Tavily
│   ├── finance_agent.py        Agent 2: financial data with yFinance
│   └── report_agent.py         Agent 3: executive report generation
├── tools/
│   └── finance_tool.py         Custom LangChain @tool wrapping yFinance
│                               Includes comparison chart builder
├── utils/
│   ├── helpers.py              Ticker map, formatters, API key loader
│   └── pdf_export.py           ReportLab PDF generation from Markdown
├── test_agents.py              CLI test runner for individual agents
├── requirements.txt
├── .env.example
├── .gitignore
└── .streamlit/
    └── config.toml             Dark theme configuration
```

---

## Installation

### Prerequisites

- Python 3.10 or later
- A Groq API key (free at https://console.groq.com)
- A Tavily API key (1,000 free searches/month at https://app.tavily.com)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-financial-research.git
cd ai-financial-research

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys
cp .env.example .env
# Edit .env and add your GROQ_API_KEY and TAVILY_API_KEY
```

---

## Usage

### Run the Streamlit dashboard

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

### Test individual agents from the CLI

```bash
# Test all three agents
python test_agents.py --company "Infosys"

# Test a single agent
python test_agents.py --company "TCS" --agent news
python test_agents.py --company "Zomato" --agent finance
python test_agents.py --company "Nvidia" --agent report
```

### Supported companies (ticker auto-resolved)

| Input name          | Resolved ticker |
|---------------------|-----------------|
| Infosys             | INFY.NS         |
| TCS                 | TCS.NS          |
| Zomato              | ZOMATO.NS       |
| HDFC Bank           | HDFCBANK.NS     |
| ICICI Bank          | ICICIBANK.NS    |
| Reliance            | RELIANCE.NS     |
| Apple               | AAPL            |
| Microsoft           | MSFT            |
| Nvidia              | NVDA            |

Any valid Yahoo Finance ticker can also be entered directly (e.g. `MSFT`, `INFY.NS`).

---

## Deployment

### Streamlit Cloud

```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-financial-research.git
git push -u origin main
```

2. Go to https://share.streamlit.io and click **New app**.
3. Select your repository, set **Main file** to `app.py`.
4. Open **Advanced settings → Secrets** and add:

```toml
GROQ_API_KEY = "gsk_..."
TAVILY_API_KEY = "tvly-..."
```

5. Click **Deploy**.

### Environment variables

| Variable       | Description                              | Required |
|----------------|------------------------------------------|----------|
| GROQ_API_KEY   | Groq API key for Llama 3.3 70B           | Yes      |
| TAVILY_API_KEY | Tavily API key for web search            | Yes      |

---

## Tech Stack

| Technology      | Version | Purpose                         |
|-----------------|---------|---------------------------------|
| Python          | 3.10+   | Runtime                         |
| LangChain       | 0.3.x   | Agent orchestration             |
| langchain-groq  | 0.3.x   | Groq LLM integration            |
| Groq / Llama    | 3.3 70B | Language model for all 3 agents |
| Tavily Python   | 0.5.x   | Web search API                  |
| yFinance        | 0.2.x   | Yahoo Finance data              |
| Plotly          | 6.x     | Interactive charts              |
| ReportLab       | 4.x     | PDF generation                  |
| Streamlit       | 1.45.x  | Web dashboard                   |
| python-dotenv   | 1.x     | Environment variable loading    |

---

## Portfolio Features

This project demonstrates the following skills relevant to AI/ML engineering roles:

- **Multi-agent orchestration** with LangChain `AgentExecutor` and `create_tool_calling_agent`
- **Custom LangChain tools** using the `@tool` decorator with structured JSON output
- **LLM chain composition** using `ChatPromptTemplate | LLM | StrOutputParser`
- **Real-time data integration** combining web search (Tavily) and financial APIs (yFinance)
- **Programmatic PDF generation** with ReportLab from parsed Markdown
- **Streamlit session state** for persistent research history within a session
- **Responsive multi-mode UI**: single company research and two-company comparison
- **Normalised price comparison charts** using indexed return (base = 100)

---

## Future Improvements

- Add a fundamental screening agent that filters stocks against user-defined criteria
- Integrate SEC EDGAR or BSE filings for earnings call transcript analysis
- Add portfolio-level analysis: run all agents across a watchlist in batch
- Cache yFinance responses with TTL to reduce redundant API calls
- Add a sentiment score timeline chart from historical news
- Support voice input for company name via Streamlit's `st.audio`

---

## Disclaimer

This system is for educational and informational purposes only. AI-generated research reports do not constitute financial or investment advice. Always conduct independent due diligence before making any investment decisions.
