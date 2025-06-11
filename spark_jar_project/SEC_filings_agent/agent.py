from google.adk.agents import Agent
from scraper import scrape_sec_filings
from summarize import summarize_filing_texts


root_agent = Agent(
    name="filings_agent",
    model="gemini-2.0-flash",
    description="Filings agent",
    instruction="""
    You are a helpful assistant that can use the following tools:
    - scraper: Get recent 10-K filings for a company and extract specific items.
    - summarize: Summarize the extracted filing texts into a comprehensive report.
    """,
    tools=[scrape_sec_filings, summarize_filing_texts],
)