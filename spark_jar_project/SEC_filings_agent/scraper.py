#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def scrape_sec_filings(company_name: str, max_filings=1):
    """
    Scrapes recent 10-K filings from SEC EDGAR for a given company name.
    
    Returns: List of file paths to extracted text sections (Item 1, 1A, 7)
    """
    output_files = []
    headers = {'User-Agent': os.getenv("SEC_USER_AGENT")}

    # Step 1: Get CIK
    cik_url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(cik_url, headers=headers)
    data = response.json()
    for entry in data.values():
        if entry['title'].lower() == company_name.lower():
            CIK = str(entry['cik_str']).zfill(10)
            break
    else:
        raise ValueError(f"CIK not found for company: {company_name}")

    # Step 2: Fetch recent filings
    sub_url = f'https://data.sec.gov/submissions/CIK{CIK}.json'
    response = requests.get(sub_url, headers=headers)
    data = response.json()
    company_filings = data['filings']['recent']

    base_url = 'https://www.sec.gov/Archives/edgar/data'
    filing_urls = []
    for accession_no, form_type in zip(company_filings['accessionNumber'], company_filings['form']):
        if form_type == '10-K':
            acc_no_nodashes = accession_no.replace('-', '')
            filing_url = f"{base_url}/{int(CIK)}/{acc_no_nodashes}/{accession_no}.txt"
            filing_urls.append((accession_no, filing_url))
        if len(filing_urls) >= max_filings:
            break

    os.makedirs("output", exist_ok=True)
    regex = re.compile(r'item\s*(1a|1b|1|7a|7|8)[\.\:\s]', re.IGNORECASE)

    for accession_no, url in filing_urls:
        r = requests.get(url, headers=headers)
        raw_10k = r.text

        # Extract <DOCUMENT> section
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

        def extract_item_text(start, end):
            return BeautifulSoup(document['10-K'][start:end], 'lxml').get_text("\n\n")

        sections = {
            "item1": ("item1", "item1a"),
            "item1a": ("item1a", "item1b"),
            "item7": ("item7", "item7a")
        }

        for section, (start_key, end_key) in sections.items():
            try:
                text = extract_item_text(pos_dat['start'].loc[start_key], pos_dat['start'].loc[end_key])
                path = f"output/{accession_no}_{section}.txt"
                with open(path, "w") as f:
                    f.write(text)
                output_files.append(path)
            except KeyError:
                continue

    return output_files


