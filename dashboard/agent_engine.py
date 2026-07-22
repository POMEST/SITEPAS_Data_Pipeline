import pandas as pd
import google.generativeai as genai
import os

def tanya_ai_gemini(pertanyaan, api_key):
    if not api_key:
        return "Maaf, API Key Gemini tidak ditemukan di pengaturan."
    
    try:
        # 1. Konfigurasi SDK Google Gemini
        genai.configure(api_key=api_key)
        
        # Menggunakan model yang PASTI TERSEDIA di akun Anda (gemini-2.5-flash)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # 2. Mengambil Super-Tabel (Master Data Lengkap)
        path_data = os.path.join('data', 'processed', 'master_seluruh_data_2025_lengkap.csv')
        
        # Cek apakah file benar-benar ada
        if not os.path.exists(path_data):
            return f"Maaf, sistem tidak menemukan file {path_data}. Pastikan proses ETL sudah berhasil."
            
        df_master = pd.read_csv(path_data)
        
        # 3. Ubah data menjadi format Teks CSV agar bisa dibaca AI
        # (Format CSV murni sangat disukai oleh LLM dan hemat token)
        data_teks = df_master.to_csv(index=False)
        
        # 4. Merancang Instruksi Sistem (Prompt) yang sangat ketat
        prompt = f"""
        Anda adalah Asisten Analis Ahli di Biro Perencanaan BPS.
        Tugas Anda adalah menjawab pertanyaan pengguna HANYA berdasarkan DATABASE RENCANA AKSI 2025 di bawah ini.
        
        DATABASE (Format CSV):
        {data_teks}
        
        ATURAN MUTLAK:
        1. Anda dilarang keras mengarang jawaban (halusinasi). Jika informasi yang ditanyakan tidak ada dalam database, jawab dengan "Informasi tersebut tidak terdapat dalam data Rencana Aksi 2025".
        2. Jika pengguna menanyakan angka capaian atau target, baca baris datanya dengan sangat teliti.
        3. Gunakan bahasa Indonesia yang formal, ringkas, dan jelas.
        4. Gunakan poin-poin (bullet points) jika menjabarkan lebih dari 2 hal/data.
        
        Pertanyaan Pengguna: "{pertanyaan}"
        """
        
        # 5. Meminta AI menjawab (Hanya butuh 1 request, anti-error parsing)
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"Maaf, terjadi kesalahan teknis pada sistem AI: {e}"