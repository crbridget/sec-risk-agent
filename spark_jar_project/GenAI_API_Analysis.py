from google import genai
from google.genai.types import HttpOptions
import os

os.environ["GOOGLE_CLOUD_PROJECT"] = "sparkjar-sec-filings"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

client = genai.Client(http_options=HttpOptions(api_version="v1"))

# Folder with text files
folder_path = "/Users/bridgetcrampton/spark_jar_project/output"
file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".txt")]

# Summarize each file
for path in file_paths:
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()
        print(f"\n📄 Summarizing: {os.path.basename(path)}")

        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=f"Please summarize the following text:\n\n{content[:20000]}"  # limit to 20k chars for safety
            )
            print("📝 Summary:\n", response.text[:1000], "\n")  # show only first 1000 chars of summary
        except Exception as e:
            print("❌ Error summarizing file:", e)