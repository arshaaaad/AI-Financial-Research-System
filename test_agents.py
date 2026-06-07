#!/usr/bin/env python3
"""
test_agents.py — Command-line agent test runner

Usage:
    python test_agents.py --company "Infosys"
    python test_agents.py --company "TCS" --agent news
    python test_agents.py --company "Zomato" --agent finance
    python test_agents.py --company "Infosys" --agent all
"""

import argparse
import json

parser = argparse.ArgumentParser(description="Test AI Financial Research Agents.")
parser.add_argument("--company", "-c", type=str, default="Infosys")
parser.add_argument("--agent", "-a", type=str, choices=["news", "finance", "report", "all"], default="all")
args = parser.parse_args()

COMPANY = args.company
AGENT   = args.agent
SEP     = "=" * 70


def section(title):
    print(f"\n{SEP}\n  {title}\n{SEP}")


def test_news(company):
    section(f"Agent 1 — News Research: {company}")
    from agents.news_agent import run_news_agent
    result = run_news_agent(company)
    print(result)
    return result


def test_finance(company):
    section(f"Agent 2 — Financial Data: {company}")
    from agents.finance_agent import run_finance_agent
    result = run_finance_agent(company)
    print(result["summary"])
    raw = {k: v for k, v in result.get("raw_data", {}).items() if k != "history_data"}
    print("\nRaw data:\n", json.dumps(raw, indent=2))
    print("\nChart generated:", result.get("chart") is not None)
    return result


def test_report(company, news_summary, finance_summary):
    section(f"Agent 3 — Executive Report: {company}")
    from agents.report_agent import run_report_agent
    result = run_report_agent(company_name=company, news_summary=news_summary, finance_summary=finance_summary)
    print(result)
    return result


def main():
    print(f"\n{SEP}\n  AI Financial Research System — Test Runner\n  Company: {COMPANY} | Mode: {AGENT.upper()}\n{SEP}")

    if AGENT == "news":
        test_news(COMPANY)
    elif AGENT == "finance":
        test_finance(COMPANY)
    elif AGENT == "report":
        test_report(COMPANY, "[No news — run --agent all]", "[No finance — run --agent all]")
    elif AGENT == "all":
        news = test_news(COMPANY)
        fin  = test_finance(COMPANY)
        test_report(COMPANY, news, fin.get("summary", ""))

    print(f"\n{SEP}\n  Test complete.\n{SEP}\n")


if __name__ == "__main__":
    main()
