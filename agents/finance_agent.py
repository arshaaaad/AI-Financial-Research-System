import json

import pandas as pd
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq

from tools.finance_tool import build_stock_chart, get_financial_data
from utils.helpers import get_api_key


def create_finance_agent() -> AgentExecutor:
    groq_api_key = get_api_key("GROQ_API_KEY")

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        groq_api_key=groq_api_key,
    )

    tools = [get_financial_data]

    system_prompt = """You are a professional financial data analyst.

Your task is to fetch and present key financial metrics for a company.

Steps:
1. Call the get_financial_data tool with the company name provided.
2. Interpret the returned JSON data.
3. Present a clean, human-readable financial summary.

Format your response exactly as follows:

**Financial Summary: {{Company Name}} ({{TICKER}})**

| Metric          | Value |
|-----------------|-------|
| Current Price   | ...   |
| Market Cap      | ...   |
| P/E Ratio       | ...   |
| Annual Revenue  | ...   |
| EPS             | ...   |
| Profit Margin   | ...   |
| Debt/Equity     | ...   |
| Return on Equity| ...   |
| 52-Week High    | ...   |
| 52-Week Low     | ...   |
| Dividend Yield  | ...   |
| 6-Month Return  | ...   |

**Quick Analysis:**
Write 2 to 3 sentences interpreting what these numbers suggest for an investor.
If any value is N/A, note that it was unavailable from Yahoo Finance."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        max_iterations=3,
        handle_parsing_errors=True,
    )


def run_finance_agent(company_name: str) -> dict:
    agent = create_finance_agent()

    user_input = (
        f"Fetch and analyse financial data for {company_name}. "
        f"Use the get_financial_data tool."
    )

    output = {"summary": "", "raw_data": {}, "chart": None}

    try:
        response = agent.invoke({"input": user_input})
        output["summary"] = response.get("output", "No summary generated.")

        raw_json = get_financial_data.invoke({"company_name": company_name})
        raw_data = json.loads(raw_json)
        output["raw_data"] = raw_data

        if raw_data.get("history_available") and raw_data.get("history_data"):
            history_df = pd.DataFrame(raw_data["history_data"])
            history_df["Date"] = pd.to_datetime(history_df["Date"])
            history_df = history_df.set_index("Date")
            output["chart"] = build_stock_chart(raw_data["ticker"], history_df)

    except Exception as exc:
        output["summary"] = f"Finance Agent error: {str(exc)}"

    return output
