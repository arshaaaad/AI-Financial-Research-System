from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from utils.helpers import get_api_key


def create_news_agent() -> AgentExecutor:
    groq_api_key = get_api_key("GROQ_API_KEY")
    tavily_api_key = get_api_key("TAVILY_API_KEY")

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        groq_api_key=groq_api_key,
    )

    search_tool = TavilySearchResults(
        max_results=6,
        tavily_api_key=tavily_api_key,
    )
    tools = [search_tool]

    system_prompt = """You are a senior financial news research analyst.

Use the search tool to find the latest news about the company the user mentions.
Run two searches:
- "[company name] latest news 2025 2026"
- "[company name] earnings results quarterly financial"

After searching, respond ONLY with the structured summary below.
Do NOT show your reasoning, steps, or intermediate analysis.
Do NOT say "Step 1", "Step 2", "The search results show", or "The final answer is".
Output the summary directly and nothing else.

Use this exact format:

**Top Headlines**
- [headline 1]
- [headline 2]
- [headline 3]
- [headline 4]

**Key Developments**
[1 to 2 paragraphs on the most important business, financial, or strategic updates]

**Market Sentiment**
[One sentence stating whether sentiment is positive, neutral, or negative, and the main reason]

**Sources**
- [URL 1]
- [URL 2]
- [URL 3]"""

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
        max_iterations=5,
        handle_parsing_errors=True,
    )


def run_news_agent(company_name: str) -> str:
    agent = create_news_agent()
    user_input = (
        f"Find and summarise the latest news about {company_name}. "
        f"Focus on recent financial results, strategic announcements, and market updates. "
        f"Return only the formatted summary — no steps, no reasoning."
    )
    try:
        response = agent.invoke({"input": user_input})
        return response.get("output", "No news summary was generated.")
    except Exception as exc:
        return f"News Agent error: {str(exc)}"
