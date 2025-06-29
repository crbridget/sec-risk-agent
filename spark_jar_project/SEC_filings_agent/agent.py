from google.adk.agents import Agent
from . import scraper
from . import summarize

root_agent = Agent(
    name="filings_agent",
    model="gemini-2.0-flash",
    description="Filings agent",
    instruction="""
    You are a helpful assistant that must always use the tools below to perform your tasks.

    1. If the user provides a CIK, first call the `scrape_sec_filings` tool to download the latest 10-K text files.
    2. After scraping, automatically call `summarize_filing_texts` using the file paths returned from the scraper.
    3. Present the final summary clearly.

    Only respond after both steps are completed.
    """,
    tools=[
        scraper.scrape_sec_filings,
        summarize.summarize_filing_texts,
    ],
)
