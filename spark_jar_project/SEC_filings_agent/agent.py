import os
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai.types import HttpOptions

load_dotenv()
headers = {'User-Agent': os.getenv("SEC_USER_AGENT")}

# Set environment variables
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("GOOGLE_CLOUD_PROJECT")
os.environ["GOOGLE_CLOUD_LOCATION"] = os.getenv("GOOGLE_CLOUD_LOCATION")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = os.getenv("GOOGLE_GENAI_USE_VERTEXAI")

client = genai.Client(http_options=HttpOptions(api_version="v1"))

def scrape_and_save_filings(CIK):
    url = f'https://data.sec.gov/submissions/CIK{CIK}.json'
    headers = {'User-Agent': os.getenv("SEC_USER_AGENT")}
    response = requests.get(url, headers=headers)
    data = response.json()

    base_url = 'https://www.sec.gov/Archives/edgar/data'
    company_filings = data['filings']['recent']
    filing_urls = []

    for accession_no, form_type in zip(company_filings['accessionNumber'], company_filings['form']):
        if form_type == '10-K':
            acc_no_nodashes = accession_no.replace('-', '')
            filing_url = f"{base_url}/{int(CIK)}/{acc_no_nodashes}/{accession_no}.txt"
            filing_urls.append((accession_no, filing_url))

    os.makedirs("output", exist_ok=True)

    regex = re.compile(r'item\s*(1a|1b|1|7a|7|8)[\.\:\s]', re.IGNORECASE)

    for accession_no, url in filing_urls:
        r = requests.get(url, headers=headers)
        raw_10k = r.text

        doc_start_pattern = re.compile(r'<DOCUMENT>')
        doc_end_pattern = re.compile(r'</DOCUMENT>')
        type_pattern = re.compile(r'<TYPE>[^\n]+')

        doc_start_is = [x.end() for x in doc_start_pattern.finditer(raw_10k)]
        doc_end_is = [x.start() for x in doc_end_pattern.finditer(raw_10k)]
        doc_types = [x[len('<TYPE>'):] for x in type_pattern.findall(raw_10k)]

        document = {}
        for doc_type, doc_start, doc_end in zip(doc_types, doc_start_is, doc_end_is):
            if doc_type.strip().upper().startswith('10-K'):
                document['10-K'] = raw_10k[doc_start:doc_end]

        if '10-K' not in document:
            continue

        matches = list(regex.finditer(document['10-K']))
        test_df = pd.DataFrame(
            [(x.group().lower().replace(' ', '').replace('.', '').replace('>', ''), x.start(), x.end()) for x in matches],
            columns=['item', 'start', 'end']
        )

        pos_dat = test_df.sort_values('start', ascending=True).drop_duplicates('item', keep='last')
        pos_dat.set_index('item', inplace=True)

        def extract_item_text(item_start, item_end):
            raw = document['10-K'][item_start:item_end]
            return BeautifulSoup(raw, 'lxml').get_text("\n\n")

        try:
            item1_text = extract_item_text(pos_dat['start'].loc['item1'], pos_dat['start'].loc['item1a'])
            with open(f"output/{accession_no}_item1.txt", "w") as f:
                f.write(item1_text)
        except KeyError:
            pass

        try:
            item1a_text = extract_item_text(pos_dat['start'].loc['item1a'], pos_dat['start'].loc['item1b'])
            with open(f"output/{accession_no}_item1a.txt", "w") as f:
                f.write(item1a_text)
        except KeyError:
            pass

        try:
            item7_text = extract_item_text(pos_dat['start'].loc['item7'], pos_dat['start'].loc['item7a'])
            with open(f"output/{accession_no}_item7.txt", "w") as f:
                f.write(item7_text)
        except KeyError:
            pass

def summarize_output():
    folder_path = "output"
    file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".txt")]

    combined_content = ""
    for path in file_paths:
        with open(path, 'r', encoding='utf-8') as file:
            file_content = file.read()
            combined_content += f"\n\n--- {os.path.basename(path)} ---\n{file_content}"

    trimmed_content = combined_content[:20000]

    prompt = f"""
    You are a financial analyst. Carefully read the following 10-K filings and generate a comprehensive and detailed summary. Your output should include:

    1. A bullet-point list of the most critical **business risks**, grouped by type (e.g., regulatory, operational, financial).
    2. A brief overview of the **company's business model and product lines**.
    3. Any recurring themes or patterns across the filings (e.g., market trends, legal concerns, strategic shifts).
    4. Insights into the company’s **technology, R&D, and competitive advantage**.
    5. Any forward-looking statements and the cautionary language used.
    6. A concise section on **potential red flags** or unusual disclosures.

    Limit your response to no more than 1500 words.

    Here is the text to analyze:
    {trimmed_content}
    """

    try:
        print("\n📄 Summarizing all files together...\n")
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=prompt
        )
        print("📝 Combined Summary:\n", response.text[:20000])
    except Exception as e:
        print("❌ Error summarizing combined content:", e)

if __name__ == "__main__":
    cik = input("Enter 10-digit CIK to analyze (e.g., 0001318605): ")
    scrape_and_save_filings(cik)
    summarize_output()
