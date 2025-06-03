from google import genai
from google.genai.types import HttpOptions
import os

# Set environment variables
os.environ["GOOGLE_CLOUD_PROJECT"] = "sparkjar-sec-filings"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

client = genai.Client(http_options=HttpOptions(api_version="v1"))

# Folder with text files
folder_path = "/Users/bridgetcrampton/spark_jar_project/output"
file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".txt")]

# Concatenate content from all files
combined_content = ""
for path in file_paths:
    with open(path, 'r', encoding='utf-8') as file:
        file_content = file.read()
        combined_content += f"\n\n--- {os.path.basename(path)} ---\n{file_content}"

# Limit content to 20,000 characters for Gemini safety
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

# Summarize all content together
try:
    print("\n📄 Summarizing all files together...\n")
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=prompt
    )
    print("📝 Combined Summary:\n", response.text[:20000]) 
except Exception as e:
    print("❌ Error summarizing combined content:", e)


