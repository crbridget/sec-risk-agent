import os # For environment variable management and file operations
import requests # For making HTTP requests
from bs4 import BeautifulSoup # For parsing HTML and XML documents
import re # For regular expression operations
import pandas as pd # For data manipulation and analysis
from dotenv import load_dotenv # For loading environment variables from a .env file
from google import genai # For interacting with Google GenAI API
from google.genai.types import HttpOptions # For setting HTTP options for the GenAI client

load_dotenv()
headers = {'User-Agent': os.getenv("SEC_USER_AGENT")}

# Set environment variables
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("GOOGLE_CLOUD_PROJECT")
os.environ["GOOGLE_CLOUD_LOCATION"] = os.getenv("GOOGLE_CLOUD_LOCATION")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = os.getenv("GOOGLE_GENAI_USE_VERTEXAI")

client = genai.Client(http_options=HttpOptions(api_version="v1"))

def scrape_and_save_filings(CIK):
    url = f'https://data.sec.gov/submissions/CIK{CIK}.json' # URL to fetch filings for the given CIK
    headers = {'User-Agent': os.getenv("SEC_USER_AGENT")} # Set user agent for requests to comply with SEC guidelines
    response = requests.get(url, headers=headers) # Fetch the JSON data for the company's filings
    data = response.json() # Parse the JSON response to extract filing information

    base_url = 'https://www.sec.gov/Archives/edgar/data' # Base URL for accessing filing documents
    company_filings = data['filings']['recent'] # Extract recent filings from the data
    filing_urls = [] # List to hold URLs of 10-K filings

    for accession_no, form_type in zip(company_filings['accessionNumber'], company_filings['form']): # Loop through each filing
        if form_type == '10-K': # Check if the filing is a 10-K
            acc_no_nodashes = accession_no.replace('-', '') # Remove dashes from the accession number
            filing_url = f"{base_url}/{int(CIK)}/{acc_no_nodashes}/{accession_no}.txt" # Construct the URL for the filing document
            filing_urls.append((accession_no, filing_url)) # Append the accession number and URL to the list

    os.makedirs("output", exist_ok=True) # Create output directory if it doesn't exist

    regex = re.compile(r'item\s*(1a|1b|1|7a|7|8)[\.\:\s]', re.IGNORECASE) # Regex to match Item 1, 1A, 1B, 7, 7A, and 8

    for accession_no, url in filing_urls:
        r = requests.get(url, headers=headers) # Fetch the filing document
        raw_10k = r.text # Extract the raw text of the 10-K filing

        doc_start_pattern = re.compile(r'<DOCUMENT>') # Regex to find start of document
        doc_end_pattern = re.compile(r'</DOCUMENT>') # Regex to find end of document
        type_pattern = re.compile(r'<TYPE>[^\n]+') # Regex to find document type

        doc_start_is = [x.end() for x in doc_start_pattern.finditer(raw_10k)] # Find start indices of documents
        doc_end_is = [x.start() for x in doc_end_pattern.finditer(raw_10k)] # Find end indices of documents
        doc_types = [x[len('<TYPE>'):] for x in type_pattern.findall(raw_10k)] # Extract document types

        document = {} # Dictionary to hold extracted documents
        for doc_type, doc_start, doc_end in zip(doc_types, doc_start_is, doc_end_is): # Loop through each document type
            if doc_type.strip().upper().startswith('10-K'): # Check if the document is a 10-K
                document['10-K'] = raw_10k[doc_start:doc_end] # Extract the 10-K document text

        if '10-K' not in document:
            continue

        matches = list(regex.finditer(document['10-K'])) # Find all matches for the regex in the 10-K document
        test_df = pd.DataFrame( # Create a DataFrame with matches
            [(x.group().lower().replace(' ', '').replace('.', '').replace('>', ''), x.start(), x.end()) for x in matches],
            columns=['item', 'start', 'end']
        )

        pos_dat = test_df.sort_values('start', ascending=True).drop_duplicates('item', keep='last') # Sort and deduplicate the DataFrame
        pos_dat.set_index('item', inplace=True) # Set the index to 'item' for easier access

        def extract_item_text(item_start, item_end): # Extract text for a specific item
            raw = document['10-K'][item_start:item_end] # Use BeautifulSoup to parse the raw text
            return BeautifulSoup(raw, 'lxml').get_text("\n\n") # Extract text with newlines

        try:
            item1_text = extract_item_text(pos_dat['start'].loc['item1'], pos_dat['start'].loc['item1a']) # Extract Item 1 text
            with open(f"output/{accession_no}_item1.txt", "w") as f: # Save Item 1 text to file
                f.write(item1_text) # Write the text to the file
        except KeyError:
            pass

        try:
            item1a_text = extract_item_text(pos_dat['start'].loc['item1a'], pos_dat['start'].loc['item1b']) # Extract Item 1A text
            with open(f"output/{accession_no}_item1a.txt", "w") as f: # Save Item 1A text to file
                f.write(item1a_text) # Write the text to the file
        except KeyError:
            pass

        try:
            item7_text = extract_item_text(pos_dat['start'].loc['item7'], pos_dat['start'].loc['item7a']) # Extract Item 7 text
            with open(f"output/{accession_no}_item7.txt", "w") as f: # Save Item 7 text to file
                f.write(item7_text) # Write the text to the file
        except KeyError:
            pass

def summarize_output():
    folder_path = "output" # Folder containing the saved 10-K filings
    file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".txt")] # List all text files in the folder

    combined_content = ""
    for path in file_paths:
        with open(path, 'r', encoding='utf-8') as file: # Read each file
            file_content = file.read() # Get the content of the file
            combined_content += f"\n\n--- {os.path.basename(path)} ---\n{file_content}" # Combine content from all files

    trimmed_content = combined_content[:20000] # Trim to 20,000 characters for API limits

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
        response = client.models.generate_content( # Generate content using the GenAI model
            model="gemini-2.0-flash-001", # Specify the model to use
            contents=prompt # Provide the prompt for summarization
        )
        print("📝 Combined Summary:\n", response.text[:20000])
    except Exception as e:
        print("❌ Error summarizing combined content:", e)

if __name__ == "__main__": 
    cik = input("Enter 10-digit CIK to analyze (e.g., 0001318605): ") 
    scrape_and_save_filings(cik) # Scrape and save filings for the given CIK
    summarize_output() # Summarize the saved filings
