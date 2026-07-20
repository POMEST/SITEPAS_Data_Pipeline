import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

def tanya_agent_kinerja(df_gen, df_tem, df_tem_baru, pertanyaan, api_key):
    if not api_key:
        return "Maaf, API Key Gemini tidak ditemukan."

    # 1. Gunakan model PRO (gemini-2.5-pro) yang jauh lebih pintar
    # 2. Matikan Safety Settings agar Google tidak memblokir kode Python yang dibuat Agent
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest", 
        google_api_key=api_key, 
        temperature=0,
        safety_settings={
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
            "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
        }
    )

    daftar_df = [df_gen, df_tem, df_tem_baru]

    agent = create_pandas_dataframe_agent(
        llm, 
        daftar_df, 
        verbose=True, 
        allow_dangerous_code=True,
        handle_parsing_errors=True
    )
    
    instruksi = f"Jawab dalam Bahasa Indonesia. df1=General, df2=Tematik, df3=Tematik Baru. Pertanyaan: {pertanyaan}"
    
    try:
        hasil = agent.invoke(instruksi)
        return hasil['output']
    except Exception as e:
        return f"Maaf, Agent AI mengalami kendala saat menganalisis data: {e}"