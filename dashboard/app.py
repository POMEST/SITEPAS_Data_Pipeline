import streamlit as st
import pandas as pd
import os

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Dashboard Evaluasi RB 2025", layout="wide", page_icon="📈")

# 2. FUNGSI LOAD DATA FAKTUAL
@st.cache_data 
def load_data():
    def read_csv_safe(file_name):
        path = os.path.join('data', 'processed', file_name)
        if os.path.exists(path):
            return pd.read_csv(path)
        return pd.DataFrame()

    df_gen = read_csv_safe('master_general_2025.csv')
    df_tem = read_csv_safe('master_tematik_2025.csv')
    df_tem_baru = read_csv_safe('master_tematik_baru_2025.csv')
    
    return df_gen, df_tem, df_tem_baru

df_gen, df_tem, df_tem_baru = load_data()

# 3. HEADER DASHBOARD
st.title("📈 Dashboard Evaluasi Kinerja RB BPS (Tahun 2025)")
st.markdown("*Analisis Faktual Capaian, Kendala, dan Solusi Pelaksanaan Rencana Aksi Reformasi Birokrasi.*")
st.markdown("---")

tab_general, tab_tematik, tab_tematik_baru = st.tabs([
    "📊 EVALUASI RB GENERAL", 
    "🎯 EVALUASI RB TEMATIK", 
    "🚀 EVALUASI TEMATIK BARU"
])

# ==========================================
# TAB 1: EVALUASI RB GENERAL
# ==========================================
with tab_general:
    st.header("Evaluasi Kinerja RB General")
    if not df_gen.empty:
        indeks_pilihan = st.selectbox("Pilih Indikator Utama (General):", options=df_gen['indikator_utama'].dropna().unique())
        df_gen_filter = df_gen[df_gen['indikator_utama'] == indeks_pilihan]
        
        # Scorecard
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Total Rencana Aksi", len(df_gen_filter))
        with c2: st.metric("Unit/PIC Terlibat", df_gen_filter['pic_pelaksana'].nunique())
        with c3: st.metric("Rata-rata Capaian TW 4", f"{df_gen_filter['tw4_capaian'].mean():.1f}%")
        
        st.markdown("---")
        st.subheader("📌 Evaluasi Progres dan Kendala (Hingga TW 4)")
        
        for i, row in df_gen_filter.iterrows():
            with st.container(border=True):
                st.write(f"**{row['rencana_aksi_desc']}**")
                st.caption(f"PIC: {row['pic_pelaksana']}")
                
                # Visualisasi Tren TW1 - TW4 menggunakan Metric Columns
                t1, t2, t3, t4 = st.columns(4)
                t1.metric("Triwulan 1", f"{row['tw1_capaian']}%")
                t2.metric("Triwulan 2", f"{row['tw2_capaian']}%")
                t3.metric("Triwulan 3", f"{row['tw3_capaian']}%")
                t4.metric("Triwulan 4", f"{row['tw4_capaian']}%")
                
                # Menampilkan Kendala dan Solusi TW 4 jika ada
                if pd.notna(row['tw4_kendala']) and str(row['tw4_kendala']).strip() != "":
                    st.error(f"**Kendala (TW4):** {row['tw4_kendala']}")
                if pd.notna(row['tw4_solusi']) and str(row['tw4_solusi']).strip() != "":
                    st.success(f"**Solusi/Tindak Lanjut:** {row['tw4_solusi']}")
    else:
        st.warning("Data RB General 2025 belum tersedia.")

# ==========================================
# TAB 2: EVALUASI RB TEMATIK
# ==========================================
with tab_tematik:
    st.header("Evaluasi Kinerja RB Tematik (Reguler)")
    if not df_tem.empty:
        tema_pilihan = st.selectbox("Pilih Fokus Tematik:", options=df_tem['indikator_utama'].dropna().unique())
        df_tem_filter = df_tem[df_tem['indikator_utama'] == tema_pilihan]
        
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Total Rencana Aksi", len(df_tem_filter))
        with c2: st.metric("Unit/PIC Terlibat", df_tem_filter['pic_pelaksana'].nunique())
        with c3: st.metric("Rata-rata Capaian TW 4", f"{df_tem_filter['tw4_capaian'].mean():.1f}%")
        
        st.markdown("---")
        
        for i, row in df_tem_filter.iterrows():
            with st.container(border=True):
                st.write(f"**{row['rencana_aksi_desc']}**")
                st.caption(f"PIC: {row['pic_pelaksana']}")
                
                t1, t2, t3, t4 = st.columns(4)
                t1.metric("TW 1", f"{row['tw1_capaian']}%")
                t2.metric("TW 2", f"{row['tw2_capaian']}%")
                t3.metric("TW 3", f"{row['tw3_capaian']}%")
                t4.metric("TW 4", f"{row['tw4_capaian']}%")
                
                if pd.notna(row['tw4_kendala']) and str(row['tw4_kendala']).strip() != "":
                    st.error(f"**Kendala (TW4):** {row['tw4_kendala']}")
                if pd.notna(row['tw4_solusi']) and str(row['tw4_solusi']).strip() != "":
                    st.success(f"**Solusi:** {row['tw4_solusi']}")
    else:
        st.warning("Data RB Tematik 2025 belum tersedia.")

# ==========================================
# TAB 3: EVALUASI TEMATIK BARU
# ==========================================
with tab_tematik_baru:
    st.header("Evaluasi Kinerja Tematik Baru (2025)")
    if not df_tem_baru.empty:
        tema_baru_pilihan = st.selectbox("Pilih Fokus Tematik Baru:", options=df_tem_baru['indikator_utama'].dropna().unique())
        df_baru_filter = df_tem_baru[df_tem_baru['indikator_utama'] == tema_baru_pilihan]
        
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Total Rencana Aksi", len(df_baru_filter))
        with c2: st.metric("Unit/PIC Terlibat", df_baru_filter['pic_pelaksana'].nunique())
        with c3: st.metric("Rata-rata Capaian TW 4", f"{df_baru_filter['tw4_capaian'].mean():.1f}%")
        
        st.markdown("---")
        
        for i, row in df_baru_filter.iterrows():
            with st.container(border=True):
                st.write(f"**{row['rencana_aksi_desc']}**")
                st.caption(f"Penyesuaian Tema: {row['penyesuaian_tema']} | PIC: {row['pic_pelaksana']}")
                
                t1, t2, t3, t4 = st.columns(4)
                t1.metric("TW 1", f"{row['tw1_capaian']}%")
                t2.metric("TW 2", f"{row['tw2_capaian']}%")
                t3.metric("TW 3", f"{row['tw3_capaian']}%")
                t4.metric("TW 4", f"{row['tw4_capaian']}%")
                
                if pd.notna(row['tw4_kendala']) and str(row['tw4_kendala']).strip() != "":
                    st.error(f"**Kendala (TW4):** {row['tw4_kendala']}")
                if pd.notna(row['tw4_solusi']) and str(row['tw4_solusi']).strip() != "":
                    st.success(f"**Solusi:** {row['tw4_solusi']}")
    else:
        st.warning("Data Tematik Baru 2025 belum tersedia.")