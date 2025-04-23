# --- Add this preprocessing script to tag PDFs with issues ---

import os
import json
import re
from PyPDF2 import PdfReader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage

GEMINI_API_KEY = 'AIzaSyB4jbxlU5rFCkRh4GL34vPODGBKCMFF0Ys'

pdf_dir = "data/case_pdfs"
output_json = "data/case_metadata.json"

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-04-17", google_api_key=GEMINI_API_KEY)

case_meta = []

for filename in os.listdir(pdf_dir):
    if filename.lower().endswith(".pdf"):
        filepath = os.path.join(pdf_dir, filename)
        reader = PdfReader(filepath)
        text = " ".join(page.extract_text() or "" for page in reader.pages[:2])  # Limit to first 2 pages

        # Ask Gemini to extract issues
        prompt = f"""
        Analyze this case text and extract:
        1. Main legal issues (as keywords)
        2. A short summary (2-3 lines)
        
        Case text:
        {text}
        """
        try:
            response = model([HumanMessage(content=prompt)])
            result = response.content

            # Basic parsing logic
            issues_match = re.search(r"issues[:\-\s]*(.*?)(summary|$)", result, re.IGNORECASE | re.DOTALL)
            summary_match = re.search(r"summary[:\-\s]*(.*)$", result, re.IGNORECASE | re.DOTALL)
            issues = re.split(r",\s*|\n", issues_match.group(1).strip()) if issues_match else []
            summary = summary_match.group(1).strip() if summary_match else ""

            parts = filename.replace(".pdf", "").split("_")
            court = parts[0] + " " + parts[1] if len(parts) >= 4 else "Unknown"
            year = parts[2] if len(parts) >= 4 else "Unknown"
            title = "_".join(parts[3:]) if len(parts) >= 4 else filename

            case_meta.append({
                "filename": filename,
                "court": court,
                "year": year,
                "title": title,
                "issues": list(filter(None, [i.strip() for i in issues])),
                "summary": summary
            })
            
            print(f"File {filename} processed")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

# Save to JSON
with open(output_json, "w") as f:
    json.dump(case_meta, f, indent=2)

print("✅ Metadata extraction complete.")
print(f"✅ Metadata saved to {output_json}.")