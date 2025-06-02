#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 19 17:08:53 2025

@author: bridgetcrampton
"""

import os
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

# --- Step 1: Get the company's recent filings metadata from SEC EDGAR ---

CIK = '0001318605'  # Tesla's CIK (Central Index Key)
url = f'https://data.sec.gov/submissions/CIK{CIK}.json'
headers = {'User-Agent': 'bridgetcrampton117@gmail.com'}  # Required by SEC

response = requests.get(url, headers=headers)
data = response.json()

# --- Step 2: Extract 10-K filing URLs from metadata ---

base_url = 'https://www.sec.gov/Archives/edgar/data'
company_filings = data['filings']['recent']

filing_urls = []
for accession_no, form_type in zip(company_filings['accessionNumber'], company_filings['form']):
    if form_type == '10-K':  # Filter for 10-K only
        acc_no_nodashes = accession_no.replace('-', '')
        filing_url = f"{base_url}/{CIK}/{acc_no_nodashes}/{accession_no}.txt"
        filing_urls.append((accession_no, filing_url))

# Create output directory for saving results
os.makedirs("output", exist_ok=True)

# Regex to identify relevant section headers
regex = re.compile(r'item\s*(1a|1b|1|7a|7|8)[\.\:\s]', re.IGNORECASE)

# --- Step 3: Loop through each 10-K filing and extract relevant sections ---

for accession_no, url in filing_urls:
    r = requests.get(url, headers=headers)
    raw_10k = r.text  # Full text of the filing

    # --- Step 3a: Identify sections marked by <DOCUMENT> and <TYPE> tags ---
    doc_start_pattern = re.compile(r'<DOCUMENT>')
    doc_end_pattern = re.compile(r'</DOCUMENT>')
    type_pattern = re.compile(r'<TYPE>[^\n]+')

    doc_start_is = [x.end() for x in doc_start_pattern.finditer(raw_10k)]
    doc_end_is = [x.start() for x in doc_end_pattern.finditer(raw_10k)]
    doc_types = [x[len('<TYPE>'):] for x in type_pattern.findall(raw_10k)]

    # Extract the actual 10-K section of the document
    document = {}
    for doc_type, doc_start, doc_end in zip(doc_types, doc_start_is, doc_end_is):
        if doc_type.strip().upper().startswith('10-K'):
            document['10-K'] = raw_10k[doc_start:doc_end]

    if '10-K' not in document:
        continue  # Skip if no 10-K section found

    # --- Step 3b: Find where each item (Item 1, 1A, 7, etc.) appears in the 10-K text ---
    matches = list(regex.finditer(document['10-K']))
    test_df = pd.DataFrame(
        [(x.group().lower().replace(' ', '').replace('.', '').replace('>', ''), x.start(), x.end()) for x in matches],
        columns=['item', 'start', 'end']
    )

    # Sort and drop duplicate matches
    pos_dat = test_df.sort_values('start', ascending=True).drop_duplicates('item', keep='last')
    pos_dat.set_index('item', inplace=True)

    # Helper function to extract and clean a section using BeautifulSoup
    def extract_item_text(item_start, item_end):
        raw = document['10-K'][item_start:item_end]
        return BeautifulSoup(raw, 'lxml').get_text("\n\n")

    # --- Step 3c: Extract and save each item as its own .txt file ---
    try:
        item1_text = extract_item_text(pos_dat['start'].loc['item1'], pos_dat['start'].loc['item1a'])
        with open(f"output/{accession_no}_item1.txt", "w") as f:
            f.write(item1_text)
    except KeyError:
        pass  # Section not found

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

