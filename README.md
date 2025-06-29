# SEC Risk Agent

This project is part of a multi-week internship curriculum focused on building intelligent systems that extract and analyze risk disclosures from SEC filings using Python, web scraping, and generative AI tools. It culminates in a deployable web app that visualizes credit risk indicators based on public company filings.

## 🔍 Overview

The **SEC Risk Agent** extracts key sections from SEC 10-K filings (Item 1 and 7), cleans the raw text, and prepares it for analysis with Large Language Models (LLMs). It's designed to integrate with Google's Agent Development Kit (ADK) and the Vertex AI GenAI API.

### 🔧 Technologies & Tools
- Python (requests, BeautifulSoup)
- Web Scraping
- Vertex AI GenAI API (text summarization, risk extraction)
- Google Agent Development Kit (ADK)

## 🛠 How to Run the Scraper

1. **Clone the repository**:
   ```bash
   git clone https://github.com/crbridget/sec-risk-agent.git
   cd sec-risk-agent
   ```
   
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   pip install google-generativeai[adk]
   ```
   
3. Set Up Environment Variables
Create a .env file inside your agent folder (e.g. SEC_filings_agent/.env) with the following:
   ```bash
   SEC_USER_AGENT=YourUserAgentHere
   GOOGLE_CLOUD_PROJECT=your-gcp-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   ```
   
   Replace the placeholders with your actual values. The SEC_USER_AGENT should be a contact string like:
   ```bash
   Bridget Crampton (your-email@example.com)
   ```
   
4. Launch the Agent (Dev Mode)
From the project root:
   ```bash
   google-adk dev
   ```

This will start the local ADK agent and open the UI at:
   ```bash
   http://localhost:8000
   ```

6. Test the Agent
In the chat window, try a prompt like:
   ```bash
   Get the latest 10-K filings for CIK 0001652044 and summarize them.
   ```
   
The agent will:
   Call scrape_sec_filings() to download key sections
   Call summarize_filing_texts() to generate a detailed analysis

👤 Author
Bridget Crampton — intern exploring the intersection of finance, AI, and UI development.

