import pandas as pd
import os
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

def get_chatbot_agent(df_gen, df_tem, df_tem_baru):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
        
    try:
        # Tambahkan label topik agar AI bisa membedakan
        df_g = df_gen.copy()
        df_t = df_tem.copy()
        df_tb = df_tem_baru.copy()
        
        if not df_g.empty: df_g['Topik_Data'] = 'General'
        if not df_t.empty: df_t['Topik_Data'] = 'Tematik'
        if not df_tb.empty: df_tb['Topik_Data'] = 'Tematik Baru'
        
        dfs = []
        if not df_g.empty: dfs.append(df_g)
        if not df_t.empty: dfs.append(df_t)
        if not df_tb.empty: dfs.append(df_tb)
        
        if not dfs:
            return None
            
        df_all = pd.concat(dfs, ignore_index=True)
        
        llm = ChatOpenAI(temperature=0, model="gpt-4o-mini", api_key=api_key)
        
        agent = create_pandas_dataframe_agent(
            llm,
            df_all,
            verbose=True,
            allow_dangerous_code=True,
            handle_parsing_errors=True
        )
        return agent
    except Exception as e:
        print(f"Error inisialisasi AI: {e}")
        return None

def tanya_chatbot(agent, pertanyaan):
    if agent is None:
        return "Maaf, sistem AI belum siap (Periksa ketersediaan OPENAI_API_KEY di file .env atau pastikan data ada)."
    try:
        prompt = f"""
Kamu adalah asisten analis data senior di Biro Perencanaan BPS.
Dataframe yang diberikan berisi 3 topik: General, Tematik, dan Tematik Baru (bisa dibedakan dari kolom 'Topik_Data').
Data berisi informasi Rencana Aksi, Indikator, PIC, serta target dan capaian setiap triwulan.

ATURAN MENJAWAB:
1. Jawab pertanyaan berdasarkan analisis dari dataframe dengan akurat tanpa halusinasi.
2. Gunakan bahasa Indonesia yang formal, ringkas, dan jelas.
3. Tampilkan angka dengan format yang mudah dibaca (misalnya dengan pemisah ribuan).
4. Jika output berupa daftar atau tabel, gunakan format Markdown yang rapi.
5. Bersikaplah ramah dan solutif layaknya asisten profesional yang sudah "hatam" dengan data tersebut.

Pertanyaan pengguna: {pertanyaan}
"""
        response = agent.invoke(prompt)
        return response.get('output', "Maaf, AI tidak mengembalikan jawaban.")
    except Exception as e:
        return f"Maaf, terjadi kesalahan saat AI memproses data: {e}"
