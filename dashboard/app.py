import streamlit as st
import pandas as pd
import os

# 1. PENGATURAN HALAMAN
st.set_page_config(page_title="Dasbor Monev Renaksi BPS", layout="wide", page_icon="🎯")

# 2. FUNGSI MEMBACA DATA (Update: Mendukung 6 File Tematik)
@st.cache_data 
def load_data():
    # Load General
    try:
        gen_m = pd.read_csv('data/processed/master_general.csv')
        gen_m.columns = gen_m.columns.str.strip()
    except FileNotFoundError:
        gen_m = pd.DataFrame()
        
    # Load Tematik (Gabungan 6 File)
    list_tematik = []
    for i in range(1, 7):
        path = f'data/processed/master_tematik_{i}.csv'
        if os.path.exists(path):
            df_t = pd.read_csv(path)
            list_tematik.append(df_t)
            
    if list_tematik:
        tem_m = pd.concat(list_tematik, ignore_index=True)
        tem_m.columns = tem_m.columns.str.strip()
    else:
        tem_m = pd.DataFrame()
        
    return gen_m, tem_m

df_gen, df_tem = load_data()

# 3. HEADER DASHBOARD
st.title("🎯 Dashboard Executive Rencana Aksi BPS 2026")
st.markdown("*Pantau progres dan capaian Reformasi Birokrasi secara terpusat dan terukur.*")
st.markdown("---")

tab_general, tab_tematik = st.tabs(["📊 DASHBOARD RB GENERAL", "📈 DASHBOARD RB TEMATIK"])

# ==========================================
# KAMAR 1: RB GENERAL (Dengan Fitur Filter)
# ==========================================
with tab_general:
    st.header("Kinerja RB General")
    
    if not df_gen.empty:
        # Pilihan Indeks (Dropdown)
        daftar_indeks = df_gen['indikator_utama'].unique()
        indeks_pilihan = st.selectbox("🎯 Pilih Indikator Utama (Indeks):", options=daftar_indeks)
        
        # Filter data sesuai indeks terpilih
        df_gen_khusus = df_gen[df_gen['indikator_utama'] == indeks_pilihan]
        
        st.info(f"Menampilkan detail untuk Indeks: **{indeks_pilihan}**")
        
        # Scorecard Khusus Indeks Terpilih
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Total Rencana Aksi", len(df_gen_khusus))
        with c2: st.metric("Unit/PIC Terlibat", df_gen_khusus['pic_pelaksana'].nunique())
        with c3: st.metric(f"Rata-rata Progres", f"{df_gen_khusus['capaian_persen'].mean():.1f}%")
        
        st.markdown("---")
        
        # Progress Bar per Rencana Aksi
        st.subheader(f"📌 Status Progres Rencana Aksi")
        
        for i, row in df_gen_khusus.iterrows():
            st.write(f"**{row['rencana_aksi_desc']}**")
            col_text, col_bar = st.columns([1, 4])
            with col_text:
                st.caption(f"PIC: {row['pic_pelaksana']}")
            with col_bar:
                st.progress(int(row['capaian_persen']), text=f"Capaian: {int(row['capaian_persen'])}%")
                
        st.markdown("---")
        with st.expander(f"📁 Lihat Rincian Tabel Data {indeks_pilihan}"):
            st.dataframe(df_gen_khusus, use_container_width=True)
    else:
        st.warning("Data General belum tersedia.")


# ==========================================
# KAMAR 2: RB TEMATIK 
# ==========================================
with tab_tematik:
    st.header("Kinerja RB Tematik")
    
    if not df_tem.empty:
        daftar_tema = df_tem['kategori'].unique()
        tema_pilihan = st.selectbox("🎯 Pilih Fokus Tematik:", options=daftar_tema)
        
        df_tem_khusus = df_tem[df_tem['kategori'] == tema_pilihan]
        
        st.info(f"Menampilkan metrik khusus untuk: **{tema_pilihan}**")
        
        c4, c5, c6 = st.columns(3)
        with c4: st.metric("Total Kegiatan", len(df_tem_khusus))
        with c5: st.metric("Unit/PIC Terlibat", df_tem_khusus['pic_pelaksana'].nunique())
        with c6: st.metric(f"Progres {tema_pilihan}", f"{df_tem_khusus['capaian_persen'].mean():.1f}%")
        
        st.markdown("---")
        st.subheader(f"📌 Status Progres Kegiatan - {tema_pilihan}")
        
        for i, row in df_tem_khusus.head(10).iterrows():
            st.write(f"**{row['rencana_aksi_desc']}**")
            col_text, col_bar = st.columns([1, 4])
            with col_text:
                st.caption(f"PIC: {row['pic_pelaksana']}")
            with col_bar:
                st.progress(int(row['capaian_persen']), text=f"Capaian: {int(row['capaian_persen'])}%")
                
        if len(df_tem_khusus) > 10:
            st.info(f"... dan {len(df_tem_khusus)-10} kegiatan lainnya (scroll di tabel bawah).")
            
        st.markdown("---")
        with st.expander(f"📁 Lihat Rincian Data {tema_pilihan}"):
            st.dataframe(df_tem_khusus, use_container_width=True)
    else:
        st.warning("Data Tematik belum tersedia.")