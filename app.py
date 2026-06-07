"""
AI Financial Research Multi-Agent System
app.py — Main Streamlit application

Run:  streamlit run app.py
"""

import json
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="AI Financial Research",
    page_icon="assets/favicon.png" if False else None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Header */
.app-header {
    background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 60%, #1D4ED8 100%);
    border-radius: 12px;
    padding: 2.2rem 2rem;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(255,255,255,0.06);
}
.app-header h1 {
    color: #F8FAFC;
    font-size: 1.9rem;
    font-weight: 700;
    margin: 0 0 0.35rem 0;
    letter-spacing: -0.4px;
}
.app-header p {
    color: rgba(255,255,255,0.55);
    font-size: 0.92rem;
    margin: 0;
}

/* Sidebar agent cards */
.agent-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.6rem;
}
.agent-card .agent-label {
    color: #60A5FA;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.9px;
    margin-bottom: 0.2rem;
}
.agent-card .agent-desc {
    color: rgba(255,255,255,0.65);
    font-size: 0.82rem;
    margin: 0;
}

/* Metric card */
.metric-card {
    background: #0F172A;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 0.9rem 1rem;
    text-align: center;
}
.metric-card .m-label {
    color: rgba(255,255,255,0.45);
    font-size: 0.7rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.7px;
    margin-bottom: 0.3rem;
}
.metric-card .m-value {
    color: #60A5FA;
    font-size: 1.25rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}
.metric-card .m-value.positive { color: #34D399; }
.metric-card .m-value.negative { color: #F87171; }

/* Section divider */
.divider {
    height: 1px;
    background: linear-gradient(to right, transparent, rgba(96,165,250,0.3), transparent);
    margin: 1.2rem 0;
}

/* History item */
.history-item {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 6px;
    padding: 0.6rem 0.9rem;
    margin-bottom: 0.4rem;
    cursor: pointer;
    font-size: 0.85rem;
    color: rgba(255,255,255,0.75);
}

/* Footer */
.app-footer {
    text-align: center;
    color: rgba(255,255,255,0.3);
    font-size: 0.78rem;
    padding: 1.5rem 0 0.5rem 0;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin-top: 2rem;
}

/* Comparison badge */
.compare-badge {
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.3);
    color: #34D399;
    border-radius: 20px;
    padding: 0.15rem 0.7rem;
    font-size: 0.72rem;
    font-weight: 600;
    display: inline-block;
}

div[data-testid="stStatusWidget"] { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)


# ── Session State Initialisation ──────────────────────────────────────────────
if "research_history" not in st.session_state:
    st.session_state.research_history = []  # list of dicts: {company, timestamp, report, raw_data}
if "last_result" not in st.session_state:
    st.session_state.last_result = None


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Configuration")
    st.markdown("---")

    # Mode selector
    mode = st.radio(
        "Research Mode",
        ["Single Company", "Compare Two Companies"],
        index=0,
        help="Single mode runs all 3 agents on one company. Compare mode runs the financial agent on both companies and generates a side-by-side analysis.",
    )

    st.markdown("---")
    st.markdown("### Example Companies")
    st.markdown("""
**Indian IT**
Infosys · TCS · Wipro · HCL Technologies

**Indian Consumer**
Zomato

**Indian Banking**
HDFC Bank · ICICI Bank · SBI

**US Tech**
Apple · Microsoft · Nvidia · Tesla
    """)

    st.markdown("---")
    st.markdown("### Agent Pipeline")
    st.markdown("""
<div class="agent-card">
    <div class="agent-label">Agent 1 — News Research</div>
    <div class="agent-desc">Tavily web search + Llama 3.3 70B summarisation</div>
</div>
<div class="agent-card">
    <div class="agent-label">Agent 2 — Financial Data</div>
    <div class="agent-desc">yFinance custom tool, live metrics and Plotly chart</div>
</div>
<div class="agent-card">
    <div class="agent-label">Agent 3 — Executive Report</div>
    <div class="agent-desc">LLM chain synthesises Buy / Hold / Sell report</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### API Keys Required")
    st.code("GROQ_API_KEY\nTAVILY_API_KEY", language="bash")

    # Research history
    if st.session_state.research_history:
        st.markdown("---")
        st.markdown("### Research History")
        for entry in reversed(st.session_state.research_history[-8:]):
            ts = entry.get("timestamp", "")
            company = entry.get("company", "")
            st.markdown(
                f'<div class="history-item">{company} <span style="color:rgba(255,255,255,0.35);font-size:0.72rem">{ts}</span></div>',
                unsafe_allow_html=True,
            )


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <h1>AI Financial Research System</h1>
    <p>Multi-agent pipeline powered by LangChain, Groq Llama 3.3 70B, Tavily Search, and Yahoo Finance</p>
</div>
""", unsafe_allow_html=True)


# ── Input Row ─────────────────────────────────────────────────────────────────
if mode == "Single Company":
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        company_name = st.text_input(
            "Company",
            placeholder="Enter company name, e.g. Infosys, TCS, Zomato, Nvidia ...",
            label_visibility="collapsed",
        )
    with col_btn:
        run_button = st.button("Run Research", type="primary", use_container_width=True)
    company_b = None

else:
    col_a, col_b, col_btn = st.columns([2.5, 2.5, 1])
    with col_a:
        company_name = st.text_input("Company A", placeholder="e.g. Infosys", label_visibility="visible")
    with col_b:
        company_b = st.text_input("Company B", placeholder="e.g. TCS", label_visibility="visible")
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        run_button = st.button("Compare", type="primary", use_container_width=True)


# ── Helper: render financial metric grid ─────────────────────────────────────
def render_metrics_grid(raw: dict):
    ret_val = raw.get("6m_return_pct", "N/A")
    ret_class = ""
    if ret_val != "N/A":
        try:
            ret_class = "positive" if float(ret_val) >= 0 else "negative"
            ret_display = f"{ret_val}%"
        except ValueError:
            ret_display = "N/A"
    else:
        ret_display = "N/A"

    price = raw.get("current_price", "N/A")
    currency = raw.get("currency", "")
    price_display = f"{price} {currency}".strip() if price != "N/A" else "N/A"

    row1 = st.columns(4)
    metrics_row1 = [
        ("Current Price",  price_display, ""),
        ("Market Cap",     raw.get("market_cap", "N/A"), ""),
        ("P/E Ratio",      raw.get("pe_ratio", "N/A"), ""),
        ("Revenue (TTM)",  raw.get("revenue", "N/A"), ""),
    ]
    for col, (label, value, cls) in zip(row1, metrics_row1):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="m-label">{label}</div>'
                f'<div class="m-value {cls}">{value}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    row2 = st.columns(4)
    metrics_row2 = [
        ("52W High",       raw.get("52_week_high", "N/A"), ""),
        ("52W Low",        raw.get("52_week_low", "N/A"), ""),
        ("Dividend Yield", raw.get("dividend_yield", "N/A"), ""),
        ("6-Month Return", ret_display, ret_class),
    ]
    for col, (label, value, cls) in zip(row2, metrics_row2):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="m-label">{label}</div>'
                f'<div class="m-value {cls}">{value}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Extended ratios row
    row3 = st.columns(4)
    metrics_row3 = [
        ("EPS",            raw.get("eps", "N/A"), ""),
        ("Profit Margin",  raw.get("profit_margin", "N/A"), ""),
        ("Debt / Equity",  raw.get("debt_to_equity", "N/A"), ""),
        ("Return on Equity", raw.get("roe", "N/A"), ""),
    ]
    for col, (label, value, cls) in zip(row3, metrics_row3):
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="m-label">{label}</div>'
                f'<div class="m-value {cls}">{value}</div></div>',
                unsafe_allow_html=True,
            )


# ── Run — Single Company Mode ─────────────────────────────────────────────────
if run_button and mode == "Single Company":
    if not company_name.strip():
        st.warning("Please enter a company name before running.")
        st.stop()

    company = company_name.strip()
    news_result = finance_result = report_result = None

    with st.status(f"Agent 1: Researching news for {company} ...", expanded=True) as s1:
        st.write("Searching the web for recent news and financial updates ...")
        try:
            from agents.news_agent import run_news_agent
            news_result = run_news_agent(company)
            s1.update(label=f"Agent 1 complete — news research for {company}", state="complete")
        except Exception as e:
            news_result = f"News Agent error: {e}"
            s1.update(label="Agent 1 failed.", state="error")

    with st.status(f"Agent 2: Fetching financial data for {company} ...", expanded=True) as s2:
        st.write("Connecting to Yahoo Finance ...")
        st.write("Fetching price, market cap, P/E ratio, revenue, and key ratios ...")
        st.write("Generating Plotly price chart ...")
        try:
            from agents.finance_agent import run_finance_agent
            finance_result = run_finance_agent(company)
            s2.update(label=f"Agent 2 complete — financial data for {company}", state="complete")
        except Exception as e:
            finance_result = {"summary": f"Finance Agent error: {e}", "raw_data": {}, "chart": None}
            s2.update(label="Agent 2 failed.", state="error")

    with st.status(f"Agent 3: Generating executive report for {company} ...", expanded=True) as s3:
        st.write("Llama 3.3 70B is synthesising news and financial data ...")
        st.write("Generating Buy / Hold / Sell recommendation ...")
        try:
            from agents.report_agent import run_report_agent
            report_result = run_report_agent(
                company_name=company,
                news_summary=news_result or "No news data available.",
                finance_summary=finance_result.get("summary", "No financial data available."),
            )
            s3.update(label=f"Agent 3 complete — executive report ready", state="complete")
        except Exception as e:
            report_result = f"Report Agent error: {e}"
            s3.update(label="Agent 3 failed.", state="error")

    # Save to history
    st.session_state.research_history.append({
        "company": company,
        "timestamp": datetime.now().strftime("%d %b %Y %H:%M"),
        "report": report_result,
        "raw_data": finance_result.get("raw_data", {}) if finance_result else {},
    })
    st.session_state.last_result = {
        "company": company,
        "news": news_result,
        "finance": finance_result,
        "report": report_result,
    }

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown(f"## Research Results — {company}")

    tab_news, tab_finance, tab_report, tab_export = st.tabs([
        "Latest News",
        "Financial Data",
        "Executive Report",
        "Export",
    ])

    with tab_news:
        st.markdown("### News Research Summary")
        st.markdown(news_result or "No news data returned.")

    with tab_finance:
        st.markdown("### Financial Metrics Dashboard")
        raw = finance_result.get("raw_data", {}) if finance_result else {}

        if raw and not raw.get("error"):
            render_metrics_grid(raw)
            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        elif raw.get("error"):
            st.error(raw["error"])

        st.markdown("### Analyst Interpretation")
        st.markdown(finance_result.get("summary", "") if finance_result else "")

        chart = finance_result.get("chart") if finance_result else None
        if chart:
            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
            st.markdown("### 6-Month Price Chart")
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("Price chart unavailable — historical data could not be fetched.")

    with tab_report:
        st.markdown("### Executive Research Report")
        if report_result:
            st.markdown(report_result)
        else:
            st.info("No report generated.")
        st.markdown("---")
        st.caption(
            "This report is AI-generated for informational purposes only. "
            "It does not constitute financial or investment advice."
        )

    with tab_export:
        st.markdown("### Export Options")

        col_md, col_pdf = st.columns(2)

        with col_md:
            st.markdown("**Download as Markdown**")
            st.markdown("Plain text Markdown file, ready to paste into Notion, GitHub, or any editor.")
            if report_result:
                st.download_button(
                    label="Download Report (.md)",
                    data=report_result,
                    file_name=f"{company.replace(' ', '_')}_research_report.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

        with col_pdf:
            st.markdown("**Download as PDF**")
            st.markdown("Styled PDF with cover page, metrics table, and formatted report sections.")
            if report_result:
                try:
                    from utils.pdf_export import generate_pdf
                    pdf_bytes = generate_pdf(company_name=company, report_text=report_result)
                    st.download_button(
                        label="Download Report (.pdf)",
                        data=pdf_bytes,
                        file_name=f"{company.replace(' ', '_')}_research_report.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"PDF generation failed: {e}")
                    st.info("Ensure `reportlab` is installed: `pip install reportlab`")


# ── Run — Compare Two Companies Mode ─────────────────────────────────────────
elif run_button and mode == "Compare Two Companies":
    if not company_name.strip() or not company_b.strip():
        st.warning("Please enter both company names before comparing.")
        st.stop()

    ca = company_name.strip()
    cb = company_b.strip()

    result_a = result_b = None

    with st.status(f"Fetching financial data for {ca} ...", expanded=False) as sa:
        try:
            from agents.finance_agent import run_finance_agent
            result_a = run_finance_agent(ca)
            sa.update(label=f"Financial data for {ca} complete", state="complete")
        except Exception as e:
            result_a = {"summary": str(e), "raw_data": {}, "chart": None}
            sa.update(label=f"Failed for {ca}", state="error")

    with st.status(f"Fetching financial data for {cb} ...", expanded=False) as sb:
        try:
            from agents.finance_agent import run_finance_agent
            result_b = run_finance_agent(cb)
            sb.update(label=f"Financial data for {cb} complete", state="complete")
        except Exception as e:
            result_b = {"summary": str(e), "raw_data": {}, "chart": None}
            sb.update(label=f"Failed for {cb}", state="error")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown(
        f"## Comparison: {ca} "
        f'<span class="compare-badge">vs</span> {cb}',
        unsafe_allow_html=True,
    )

    # Side-by-side metrics
    col_a_head, col_b_head = st.columns(2)
    with col_a_head:
        st.markdown(f"### {ca}")
        raw_a = result_a.get("raw_data", {}) if result_a else {}
        if raw_a and not raw_a.get("error"):
            render_metrics_grid(raw_a)
        elif raw_a.get("error"):
            st.error(raw_a["error"])

    with col_b_head:
        st.markdown(f"### {cb}")
        raw_b = result_b.get("raw_data", {}) if result_b else {}
        if raw_b and not raw_b.get("error"):
            render_metrics_grid(raw_b)
        elif raw_b.get("error"):
            st.error(raw_b["error"])

    # Comparison chart
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("### Normalised Price Comparison (6 Months)")

    raw_a = result_a.get("raw_data", {}) if result_a else {}
    raw_b = result_b.get("raw_data", {}) if result_b else {}

    hist_a = raw_a.get("history_data")
    hist_b = raw_b.get("history_data")

    if hist_a and hist_b:
        from tools.finance_tool import build_comparison_chart

        df_a = pd.DataFrame(hist_a)
        df_a["Date"] = pd.to_datetime(df_a["Date"])
        df_a = df_a.set_index("Date")

        df_b = pd.DataFrame(hist_b)
        df_b["Date"] = pd.to_datetime(df_b["Date"])
        df_b = df_b.set_index("Date")

        comp_chart = build_comparison_chart(
            raw_a.get("ticker", ca), df_a,
            raw_b.get("ticker", cb), df_b,
        )
        st.plotly_chart(comp_chart, use_container_width=True)
    else:
        st.info("Comparison chart unavailable — historical data missing for one or both companies.")

    # Key metrics comparison table
    st.markdown("### Head-to-Head Metrics")
    metrics_keys = [
        ("Current Price",   "current_price"),
        ("Market Cap",      "market_cap"),
        ("P/E Ratio",       "pe_ratio"),
        ("Revenue (TTM)",   "revenue"),
        ("EPS",             "eps"),
        ("Profit Margin",   "profit_margin"),
        ("Return on Equity","roe"),
        ("Debt / Equity",   "debt_to_equity"),
        ("52W High",        "52_week_high"),
        ("52W Low",         "52_week_low"),
        ("Dividend Yield",  "dividend_yield"),
        ("6-Month Return",  "6m_return_pct"),
    ]

    table_data = {"Metric": [], ca: [], cb: []}
    for label, key in metrics_keys:
        table_data["Metric"].append(label)
        val_a = raw_a.get(key, "N/A") if raw_a else "N/A"
        val_b = raw_b.get(key, "N/A") if raw_b else "N/A"
        if key == "6m_return_pct" and val_a != "N/A":
            val_a = f"{val_a}%"
        if key == "6m_return_pct" and val_b != "N/A":
            val_b = f"{val_b}%"
        table_data[ca].append(val_a)
        table_data[cb].append(val_b)

    st.dataframe(
        pd.DataFrame(table_data).set_index("Metric"),
        use_container_width=True,
    )


# ── Empty state ───────────────────────────────────────────────────────────────
elif not run_button:
    st.markdown("""
<div style="text-align:center; padding: 3rem 1rem;">
    <p style="font-size:1rem; color:rgba(255,255,255,0.35); margin-top:1rem;">
        Enter a company name above and click <strong>Run Research</strong> to start the agent pipeline.
    </p>
    <p style="font-size:0.85rem; color:rgba(255,255,255,0.2); margin-top:0.5rem;">
        Suggested: Infosys &nbsp;·&nbsp; TCS &nbsp;·&nbsp; Zomato &nbsp;·&nbsp; HDFC Bank &nbsp;·&nbsp; Nvidia
    </p>
</div>
""", unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-footer">
    Built with LangChain, Groq, Tavily, yFinance, Plotly, and Streamlit.
</div>
""", unsafe_allow_html=True)
