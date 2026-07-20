import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)

if response.status_code == 200:
    models = response.json().get("models", [])
    print("\n✅ DAFTAR MODEL YANG BISA ANDA GUNAKAN:")
    for m in models:
        if "generateContent" in m.get("supportedGenerationMethods", []):
            # Hanya menampilkan nama modelnya saja
            print(f"- {m['name'].replace('models/', '')}")
    print("---------------------------------------\n")
else:
    print(f"❌ Error: {response.status_code} - {response.text}")