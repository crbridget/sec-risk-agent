#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from dotenv import load_dotenv
from requests.adapters import Retry
import time

load_dotenv()

def scrape_sec_filings(CIK: str, max_filings: int = 5) -> list:
    """
    Scrapes recent 10-K filings from SEC EDGAR for a given company CIK.
    """
    output_files = []

    session = requests.Session()
    retries = Retry(
    total=5,                     # number of retry attempts
    backoff_factor=1.0,          # delay between retries: 1s, 2s, 4s, ...
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
    )
    
    headers = {'User-Agent': os.getenv("SEC_USER_AGENT")}

    session.mount('https://', requests.adapters.HTTPAdapter(max_retries=retries))
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=retries))
    session.headers.update(headers)

    def fetch_with_retries(url):
        """Fetch a URL with retries and a timeout."""
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        time.sleep(1)                 # brief delay to respect SEC servers
        return response

    # Step 1: Fetch recent filings
    sub_url = f'https://data.sec.gov/submissions/CIK{CIK}.json'
    response = fetch_with_retries(sub_url)
    data = response.json()
    company_filings = data['filings']['recent']

    base_url = 'https://www.sec.gov/Archives/edgar/data'
    filing_urls = []
    for accession_no, form_type in zip(company_filings['accessionNumber'], company_filings['form']):
        if form_type == '10-K':
            acc_no_nodashes = accession_no.replace('-', '')
            filing_url = f"{base_url}/{int(CIK)}/{acc_no_nodashes}/{accession_no}.txt"
            filing_urls.append((accession_no, filing_url))
        if len(filing_urls) >= max_filings: # maximum number of filings to scrape is 5
            break

    os.makedirs("output", exist_ok=True) # create output directory if it doesn't already exist
    regex = re.compile(r'item\s*(1a|1b|1|7a|7|8)[\.\:\s]', re.IGNORECASE)

    for accession_no, url in filing_urls:
        r = fetch_with_retries(url)
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