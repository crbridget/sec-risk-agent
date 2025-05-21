#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 19 17:08:53 2025

@author: bridgetcrampton
"""

# import libraries
from sec_api import ExtractorApi
import requests
from bs4 import BeautifulSoup
import html

# read api key file
file = open("api_key.txt", "r")
api_key = file.read()

extractorApi = ExtractorApi(api_key)

# 10-K example
url_10k = "https://www.sec.gov/Archives/edgar/data/1318605/000156459021004599/tsla-10k_20201231.htm"

# extract Item 1.A Risk Factors from 10-K filing in text format
item_1A_text = extractorApi.get_section(url_10k, "1A", "text")

# extract Item 1 Business from 10-k filing in text format
item_1_text = extractorApi.get_section(url_10k, "1", "text")

# extract Item 7 Management’s Discussion and Analysis of Financial Condition and Results of Operations from 10-k filing in text format
item_7_text = extractorApi.get_section(url_10k, "7", "text")


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
    item_1_text = extractorApi.get_section(url, "1", "text")
    item_1A_text = extractorApi.get_section(url, "1A", "text")
    item_7_text = extractorApi.get_section(url, "7", "text")
    
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

item_1_text = clean_text(item_1_text)

def tokenize_text(text):
    '''
    Tokenizes text into sentences and words.
    
    Parameters
    ----------
    text : str
        Text from a 10-k item.

    Returns
    -------
    sentences : list
        List of sentences.
    words : list
        List of words.
    '''
    # split text into sentences
    sentences = text.split('. ')
    
    # split each sentence into words
    words = [sentence.split() for sentence in sentences]
    
    return sentences, words
print(tokenize_text(item_1_text))




