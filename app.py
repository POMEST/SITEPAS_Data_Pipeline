import streamlit as st
import pandas as pd

# 1. PENGATURAN HALAMAN (Lebih elegan)
st.set_page_config(page_title="Dasbor Renaksi BPS", layout="wide", page_icon="📈")

st.title("📊 Dashboard Monitoring Rencana Aksi BPS 2026")
st.markdown("*Platform pemantauan target capaian Reformasi Birokrasi (General & Tematik) BPS*")
st.markdown("---")

# 2. MEMBACA KEDUA DATA KITA (Master & Target)
@st.cache_data 
def load_data():
    # Mengambil data master
    df_master = pd.read_csv('data/processed/master_renaksi_bps_terintegrasi.csv')
    # Mengambil data target (yang sudah di-Unpivot/Melt)
    df_target = pd.read_csv('data/processed/target_output_terintegrasi.csv')
    return df_master, df_target

df, df_target = load_data()

# 3. MEMBUAT SIDEBAR UNTUK FILTER (Fitur Favorit Pimpinan!)
st.sidebar.header("🔍 Filter Dashboard")
st.sidebar.markdown("Gunakan menu ini untuk memfilter data:")

# Membuat Dropdown Filter Kategori Tematik
pilihan_tematik = st.sidebar.multiselect(
    "Pilih Kategori Tematik:",
    options=df['kategori_tematik'].unique(),
    default=df['kategori_tematik'].unique() # Default-nya pilih semua
)

# Menghubungkan Filter dengan Data (Data akan berubah sesuai pilihan)
df_filtered = df[df['kategori_tematik'].isin(pilihan_tematik)]
df_target_filtered = df_target[df_target['kategori_tematik'].isin(pilihan_tematik)]

# 4. MEMBUAT METRIK (Berdasarkan data yang difilter)
st.subheader("📋 Ringkasan Utama")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total Rencana Aksi", value=len(df_filtered))
with col2:
    st.metric(label="Total Kategori Aktif", value=df_filtered['kategori_tematik'].nunique())
with col3:
    st.metric(label="Total Unit Pelaksana (PIC)", value=df_filtered['pic_pelaksana'].nunique())

st.markdown("<br>", unsafe_allow_html=True) # Memberi jarak

# 5. VISUALISASI GRAFIK (Membagi layar jadi 2 sisi)
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Sebaran Rencana Aksi per Kategori")
    sebaran_kategori = df_filtered['kategori_tematik'].value_counts()
    st.bar_chart(sebaran_kategori, color="#4CAF50") # Memberi warna hijau elegan

with col_chart2:
    st.subheader("Tren Target Penyelesaian (Per Triwulan)")
    # Menggunakan tabel hasil Unpivot untuk melihat tren TW1 s.d. TW4
    tren_tw = df_target_filtered.groupby('periode_tw')['target_penyelesaian'].sum()
    st.line_chart(tren_tw, color="#FF9800") # Memberi warna oranye

st.markdown("---")

# 6. TABEL RINCIAN (Dibuat bisa buka-tutup agar tidak penuh)
st.subheader("📑 Detail Rencana Aksi")
with st.expander("Klik di sini untuk melihat/menyembunyikan tabel rincian data"):
    st.dataframe(df_filtered, use_container_width=True)

st.caption("Dikembangkan oleh [Nama Anda] - Kerja Praktik BPS RI 2026")