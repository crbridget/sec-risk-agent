#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 19 17:08:53 2025

@author: bridgetcrampton
"""

# import libraries
import requests # import requests to make HTTP requests
from bs4 import BeautifulSoup # import BeautifulSoup to parse HTML
import re # import re module for REGEXes
import pandas as pd
import html


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

for accession_no, form_type in zip(company_filings['accessionNumber'], company_filings['form']):
    if form_type == '10-K':
        acc_no_nodashes = accession_no.replace('-', '')
        # Build .txt URL using both versions of accession number
        filing_url = f"{base_url}/{CIK}/{acc_no_nodashes}/{accession_no}.txt"
        filing_urls.append(filing_url)

# Save the URLs to a text file
with open("tesla_10k_urls.txt", "w") as f:
    for url in filing_urls:
        f.write(url + "\n")

''' extract text '''
for url in filing_urls:
    r = requests.get(url, headers=headers)
    raw_10k = r.text
    print(raw_10k[0:1300])

# Regex to find <DOCUMENT> tags
doc_start_pattern = re.compile(r'<DOCUMENT>')
doc_end_pattern = re.compile(r'</DOCUMENT>')
# Regex to find <TYPE> tag prceeding any characters, terminating at new line
type_pattern = re.compile(r'<TYPE>[^\n]+')

# Create 3 lists with the span idices for each regex

### There are many <Document> Tags in this text file, each as specific exhibit like 10-K, EX-10.17 etc
### First filter will give us document tag start <end> and document tag end's <start> 
### We will use this to later grab content in between these tags
doc_start_is = [x.end() for x in doc_start_pattern.finditer(raw_10k)]
doc_end_is = [x.start() for x in doc_end_pattern.finditer(raw_10k)]

### Type filter is interesting, it looks for <TYPE> with Not flag as new line, ie terminare there, with + sign
### to look for any char afterwards until new line \n. This will give us <TYPE> followed Section Name like '10-K'
### Once we have have this, it returns String Array, below line will with find content after <TYPE> ie, '10-K' 
### as section names
doc_types = [x[len('<TYPE>'):] for x in type_pattern.findall(raw_10k)]
    
document = {}

# Create a loop to go through each section type and save only the 10-K section in the dictionary
for doc_type, doc_start, doc_end in zip(doc_types, doc_start_is, doc_end_is):
    normalized_type = doc_type.strip().upper()
    if normalized_type.startswith('10-K'):
        document['10-K'] = raw_10k[doc_start:doc_end]


# Write the regex
regex = re.compile(r'(>Item(\s|&#160;|&nbsp;)(1A|1B|7A|7|8)\.{0,1})|(ITEM\s(1A|1B|7A|7|8))')

# Use finditer to math the regex
matches = regex.finditer(document['10-K'])

# Write a for loop to print the matches
for match in matches:
    print(match)

# Matches
matches = regex.finditer(document['10-K'])

# Create the dataframe
test_df = pd.DataFrame([(x.group(), x.start(), x.end()) for x in matches])

test_df.columns = ['item', 'start', 'end']
test_df['item'] = test_df.item.str.lower()

# Display the dataframe
print(test_df.head())

# Get rid of unnesesary charcters from the dataframe
test_df.replace('&#160;',' ',regex=True,inplace=True)
test_df.replace('&nbsp;',' ',regex=True,inplace=True)
test_df.replace(' ','',regex=True,inplace=True)
test_df.replace('\.','',regex=True,inplace=True)
test_df.replace('>','',regex=True,inplace=True)

# display the dataframe
print(test_df.head())

# Drop duplicates
pos_dat = test_df.sort_values('start', ascending=True).drop_duplicates(subset=['item'], keep='last')

# Display the dataframe
print(pos_dat)

# Set item as the dataframe index
pos_dat.set_index('item', inplace=True)

# display the dataframe
print(pos_dat)

# Get Item 1a
item_1a_raw = document['10-K'][pos_dat['start'].loc['item1a']:pos_dat['start'].loc['item1b']]

# Get Item 7
item_7_raw = document['10-K'][pos_dat['start'].loc['item7']:pos_dat['start'].loc['item7a']]

print(item_1a_raw[0:1000])

# Apply BeautifulSoup to clean the text

### First convert the raw text we have to exrtacted to BeautifulSoup object 
item_1a_content = BeautifulSoup(item_1a_raw, 'lxml')

### By just applying .pretiffy() we see that raw text start to look oragnized, as BeautifulSoup
### apply indentation according to the HTML Tag tree structure
print(item_1a_content.prettify()[0:1000])

### Our goal is though to remove html tags and see the content
### Method get_text() is what we need, \n\n is optional, I just added this to read text 
### more cleanly, it's basically new line character between sections. 
print(item_1a_content.get_text("\n\n")[0:1500])

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