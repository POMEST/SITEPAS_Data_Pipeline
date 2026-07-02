import streamlit as st
import pandas as pd

# 1. Pengaturan Halaman
st.set_page_config(page_title="Dashboard Renaksi BPS", layout="wide")
st.title("📊 Dashboard Monitoring Rencana Aksi BPS 2026")
st.markdown("---")

# 2. Membaca Data
@st.cache_data 
def load_data():
    df_master = pd.read_csv('data/processed/master_renaksi_bps_terintegrasi.csv')
    return df_master

df = load_data()

# 3. MEMBUAT METRIK (SCORECARD)
st.subheader("Ringkasan Utama")
# Kita bagi layar menjadi 3 kolom
col1, col2, col3 = st.columns(3)

# Menghitung angka-angkanya menggunakan Pandas
total_kegiatan = len(df)
total_tematik = df['kategori_tematik'].nunique()
total_pic = df['pic_pelaksana'].nunique()

# Menampilkan angka ke masing-masing kolom
with col1:
    st.metric(label="Total Rencana Aksi", value=total_kegiatan)
with col2:
    st.metric(label="Total Kategori", value=total_tematik)
with col3:
    st.metric(label="Total Unit Pelaksana (PIC)", value=total_pic)

st.markdown("---")

# 4. MEMBUAT GRAFIK BATANG (BAR CHART)
st.subheader("Sebaran Rencana Aksi per Kategori")

# Menghitung jumlah baris untuk setiap kategori tematik
sebaran_kategori = df['kategori_tematik'].value_counts()

# Menampilkan grafik batang (otomatis dibuat oleh Streamlit!)
st.bar_chart(sebaran_kategori)

st.markdown("---")

# 5. MENAMPILKAN TABEL RINCIAN
st.subheader("Tabel Rincian Data")
st.dataframe(df)