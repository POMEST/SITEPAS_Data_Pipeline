import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Dashboard Evaluasi RB 2025", layout="wide", page_icon="📈")

@st.cache_data 
def load_data():
    def read_csv_safe(file_name):
        path = os.path.join('data', 'processed', file_name)
        if os.path.exists(path): return pd.read_csv(path)
        return pd.DataFrame()
    return read_csv_safe('master_general_2025.csv'), read_csv_safe('master_tematik_2025.csv'), read_csv_safe('master_tematik_baru_2025.csv')

df_gen, df_tem, df_tem_baru = load_data()

def tampilkan_scorecard(df_filter):
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Total Rencana Aksi", len(df_filter))
    with c2: st.metric("Unit/PIC Terlibat", df_filter['pic_pelaksana'].nunique())
    
    # --- PERBAIKAN ERROR TypeError ---
    valid_rows = df_filter[df_filter['tw4_status'] == 'Normal']
    if not valid_rows.empty:
        rata_capaian = valid_rows['tw4_capaian'].astype(float).mean()
        rata_text = f"{rata_capaian:.1f}%"
    else:
        rata_text = "Tidak ada target"
        
    with c3: st.metric("Rata-rata Capaian TW 4", rata_text)
    st.markdown("---")

def tampilkan_card_rencana_aksi(row, is_tematik_baru=False):
    with st.container(border=True):
        st.write(f"**{row['rencana_aksi_desc']}**")
        if is_tematik_baru and 'penyesuaian_tema' in row and pd.notna(row['penyesuaian_tema']):
            st.caption(f"Penyesuaian Tema: {row['penyesuaian_tema']} | PIC: {row['pic_pelaksana']}")
        else:
            st.caption(f"PIC: {row['pic_pelaksana']}")
            
        st.markdown("---")
        t_cols = st.columns(4)
        for tw in range(1, 5):
            with t_cols[tw-1]:
                st.markdown(f"**Triwulan {tw}**")
                status = row.get(f'tw{tw}_status', '-')
                capaian = row.get(f'tw{tw}_capaian', 0.0)
                
                try: capaian_val = float(capaian)
                except: capaian_val = 0.0
                
                if status == "Belum Ada Target":
                    st.markdown("⚪ *Belum ada target*")
                elif status == "Tercapai Lebih Awal":
                    st.success(f"⭐ **{capaian_val:.0f}%** (Lebih Awal)")
                elif status == "Normal":
                    st.metric(label="", value=f"{capaian_val:.0f}%", label_visibility="collapsed")
                    st.progress(min(capaian_val / 100.0, 1.0))
                else:
                    st.markdown("-")
                    
        if 'tw4_kendala' in row and pd.notna(row['tw4_kendala']) and str(row['tw4_kendala']).strip() != "":
            st.error(f"🚨 **Kendala (TW 4):** {row['tw4_kendala']}")
        if 'tw4_solusi' in row and pd.notna(row['tw4_solusi']) and str(row['tw4_solusi']).strip() != "":
            st.info(f"💡 **Solusi:** {row['tw4_solusi']}")

st.title("📈 Dashboard Evaluasi Kinerja RB BPS (Tahun 2025)")
st.markdown("---")

tab_general, tab_tematik, tab_tematik_baru = st.tabs(["📊 EVALUASI RB GENERAL", "🎯 EVALUASI RB TEMATIK", "🚀 EVALUASI TEMATIK BARU"])

with tab_general:
    if not df_gen.empty:
        indeks = st.selectbox("Pilih Indikator Utama (General):", options=df_gen['indikator_utama'].dropna().unique())
        df_filter = df_gen[df_gen['indikator_utama'] == indeks]
        tampilkan_scorecard(df_filter)
        for _, row in df_filter.iterrows(): tampilkan_card_rencana_aksi(row)

with tab_tematik:
    if not df_tem.empty:
        tema = st.selectbox("Pilih Fokus Tematik:", options=df_tem['indikator_utama'].dropna().unique())
        df_filter = df_tem[df_tem['indikator_utama'] == tema]
        tampilkan_scorecard(df_filter)
        for _, row in df_filter.iterrows(): tampilkan_card_rencana_aksi(row)

with tab_tematik_baru:
    if not df_tem_baru.empty:
        tema_baru = st.selectbox("Pilih Fokus Tematik Baru:", options=df_tem_baru['indikator_utama'].dropna().unique())
        df_filter = df_tem_baru[df_tem_baru['indikator_utama'] == tema_baru]
        tampilkan_scorecard(df_filter)
        for _, row in df_filter.iterrows(): tampilkan_card_rencana_aksi(row, is_tematik_baru=True)