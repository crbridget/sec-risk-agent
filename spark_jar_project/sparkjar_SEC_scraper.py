#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 19 17:08:53 2025

@author: bridgetcrampton
"""

# import libraries
import requests
from bs4 import BeautifulSoup
import html
import subprocess


''' extract filings URLs '''

# request the filings
CIK = '0001318605'  # Tesla
url = f'https://data.sec.gov/submissions/CIK{CIK}.json'

headers = {'User-Agent': 'bridgetcrampton117@gmail.com'}

response = requests.get(url, headers=headers)
data = response.json()

# extract filings URLs
base_url = 'https://www.sec.gov/Archives/edgar/data'
company_filings = data['filings']['recent']

filing_urls = []

# loop through the filings and extract the URLs for 10-K forms
for accession_no, form_type in zip(company_filings['accessionNumber'], company_filings['form']):
    if form_type == '10-K':  
        acc_no_formatted = accession_no.replace('-', '')
        filing_url = f"{base_url}/{CIK}/{acc_no_formatted}/{accession_no}-index.htm"
        filing_urls.append(filing_url)

print(filing_urls)

''' extract text '''

for url in filing_urls:
    print(f"\n🔍 Processing: {url}")

    try:
        # Step 1: Download the full 10-K document text
        response = requests.get(url, headers=headers)
        document_text = response.text

        # Step 2: Create the prompt for Ollama
        prompt = f"""Extract the full section titled "Item 1A. Risk Factors" from the following SEC filing. 
                Only return the section text, nothing else. 

{document_text}
"""

        result = subprocess.run(
        ["ollama", "run", "mistral"],
        input=prompt.encode(),
        capture_output=True
        )

        print("✅ Extracted Item 1A Section:")
        print(result.stdout.decode())

    except Exception as e:
        print(f"❌ Error processing {url}: {e}")
    
''' clean text '''
def clean_text(text):
    '''
    Cleans item text by removing HTML entities and tags.
    
    Parameters
    ----------
    text : str
        Text from a 10-k item.

    Returns
    -------
    clean : str
        Cleaned plain-text string.
    '''
    # convert HTML entities to actual characters
    unescaped = html.unescape(text)
    
    # remove HTML tags
    soup = BeautifulSoup(unescaped, "html.parser")
    clean = soup.get_text(separator=' ', strip=True)
    
    return clean