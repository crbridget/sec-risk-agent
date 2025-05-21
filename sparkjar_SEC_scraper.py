#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 19 17:08:53 2025

@author: bridgetcrampton
"""

# import library
from sec_api import ExtractorApi

api_key = "29c03f5a158695b860d160c8c92e1bfb022233f45acb002dcdcd8a4ed831a786"

extractorApi = ExtractorApi(api_key)

# 10-K example
url_10k = "https://www.sec.gov/Archives/edgar/data/1318605/000156459021004599/tsla-10k_20201231.htm"
# extract Item 1.A Risk Factors from 10-K filing in text format
item_1A_text = extractorApi.get_section(url_10k, "1A", "text")
# extract Item 1 Business from 10-k filing in text format
item_1_text = extractorApi.get_section(url_10k, "1", "text")
# extract Item 7 Management’s Discussion and Analysis of Financial Condition and Results of Operations from 10-k filing in text format
item_7_text = extractorApi.get_section(url_10k, "7", "text")


