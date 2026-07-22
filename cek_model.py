import os
import requests
from dotenv import load_dotenv

# Load environment variables dari file .env
load_dotenv()

# Ambil API Key Groq
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ Error: GROQ_API_KEY tidak ditemukan. Pastikan sudah ada di file .env")
    exit()

# Endpoint API Groq untuk melihat daftar model
url = "https://api.groq.com/openai/v1/models"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Kirim request GET ke API Groq
response = requests.get(url, headers=headers)

if response.status_code == 200:
    models = response.json().get("data", [])
    print("\n✅ DAFTAR MODEL GROQ YANG BISA ANDA GUNAKAN:")
    
    # Mengurutkan model berdasarkan ID agar lebih rapi (opsional)
    models_sorted = sorted(models, key=lambda x: x['id'])
    
    for m in models_sorted:
        print(f"- {m['id']}")
    print("---------------------------------------\n")
else:
    print(f"❌ Error: {response.status_code} - {response.text}")