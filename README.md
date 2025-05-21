# SEC Risk Agent

This project is part of a multi-week internship curriculum focused on building intelligent systems that extract and analyze risk disclosures from SEC filings using Python, web scraping, and generative AI tools. It culminates in a deployable web app that visualizes credit risk indicators based on public company filings.

## 🔍 Overview

The **SEC Risk Agent** extracts key sections from SEC 10-K filings (Item 1, 1A, and 7), cleans the raw text, and prepares it for analysis with Large Language Models (LLMs). It's designed to integrate with Google's Agent Development Kit (ADK) and the Vertex AI GenAI API, forming the backend of a web app built on [lovable.dev](https://www.lovable.dev).

### 🔧 Technologies & Tools
- Python (requests, BeautifulSoup)
- SEC EDGAR API / Web Scraping
- Vertex AI GenAI API (text summarization, risk extraction)
- Google Agent Development Kit (ADK)
- lovable.dev (low-code frontend)

## 📈 My Learning Journey

As an intern, I’m following a structured, multi-week progression that includes:

- **Week 1**: Learning about credit risk, SEC filings, and Python basics  
- **Week 2**: Building scrapers and preprocessing data for LLMs  
- **Week 3**: Prompt engineering and interacting with GenAI APIs  
- **Week 4–5**: Developing agent tools using Google ADK for extracting risk factors  
- **Week 6–7**: Designing and deploying a front-end web app on lovable.dev  

Each phase builds toward a functioning pipeline that connects scraped regulatory data to a GenAI-powered backend, then visualizes the results in a user-friendly interface.

## 🛠 How to Run the Scraper

1. **Clone the repository**:
   ```bash
   git clone https://github.com/crbridget/sec-risk-agent.git
   cd sec-risk-agent
   
2. Install dependencies
   ```bash
    pip install requests beautifulsoup4

4. Run the Scraper
   ```bash
    python sparkjar_SEC_scraper.py

📌 Future Steps
Wrap text-processing tools as ADK agents

Integrate GenAI output (summaries, sentiment, keyword extraction)

Build a lovable.dev frontend to input tickers and visualize results

Connect stock sentiment data for deeper context

👤 Author
Bridget Crampton — intern exploring the intersection of finance, AI, and UI development.

