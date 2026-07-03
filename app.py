import streamlit as st
import pandas as pd

# 1. PENGATURAN HALAMAN
st.set_page_config(page_title="Dasbor Renaksi BPS", layout="wide", page_icon="📈")

st.title("📊 Dashboard Monitoring Rencana Aksi BPS 2026")
st.markdown("*Platform pemantauan target capaian Reformasi Birokrasi (General & Tematik) BPS*")
st.markdown("---")

# 2. MEMBACA DATA
@st.cache_data 
def load_data():
    df_master = pd.read_csv('data/processed/master_renaksi_bps_terintegrasi.csv')
    df_target = pd.read_csv('data/processed/target_output_terintegrasi.csv')
    
    # [PERBAIKAN ERROR] Meminjam kolom 'pic_pelaksana' dari df_master ke df_target
    # Ini seperti VLOOKUP berdasarkan nomor/index agar df_target punya data PIC
    df_target = pd.merge(df_target, df_master[['kategori_tematik', 'indikator_utama', 'pic_pelaksana']], 
                         on=['kategori_tematik', 'indikator_utama'], 
                         how='left')
    return df_master, df_target

df, df_target = load_data()

# 3. SIDEBAR FILTER 
st.sidebar.header("🔍 Filter Dashboard")

tema_all = df['kategori_tematik'].dropna().unique()
pilihan_tematik = st.sidebar.multiselect("Pilih Kategori Tematik:", options=tema_all, default=tema_all)

pic_all = df['pic_pelaksana'].dropna().unique()
pilihan_pic = st.sidebar.multiselect("Pilih Unit Pelaksana (PIC):", options=pic_all, default=pic_all)

kata_kunci = st.sidebar.text_input("Cari Kata Kunci Kegiatan (opsional):", "")


# 4. MENERAPKAN FILTER KE DATA
df_filtered = df[
    (df['kategori_tematik'].isin(pilihan_tematik)) & 
    (df['pic_pelaksana'].isin(pilihan_pic))
]

if kata_kunci:
    df_filtered = df_filtered[df_filtered['rencana_aksi_desc'].str.contains(kata_kunci, case=False, na=False)]

# Sekarang df_target sudah punya kolom pic_pelaksana, filter pasti berhasil!
df_target_filtered = df_target[
    df_target['kategori_tematik'].isin(pilihan_tematik) & 
    (df_target['pic_pelaksana'].isin(pilihan_pic))
]


# 5. SCORECARD
st.subheader("📋 Ringkasan Utama")
col1, col2, col3 = st.columns(3)

with col1: st.metric(label="Total Rencana Aksi", value=len(df_filtered))
with col2: st.metric(label="Total Kategori Aktif", value=df_filtered['kategori_tematik'].nunique())
with col3: st.metric(label="Total PIC Terlibat", value=df_filtered['pic_pelaksana'].nunique())

st.markdown("<br>", unsafe_allow_html=True)


# 6. VISUALISASI BARIS PERTAMA
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Tren Target Penyelesaian (Per Triwulan)")
    tren_tw = df_target_filtered.groupby('periode_tw')['target_penyelesaian'].count()
    st.line_chart(tren_tw, color="#FF9800")

with col_chart2:
    st.subheader("Sebaran Rencana Aksi per Kategori")
    sebaran_kategori = df_filtered['kategori_tematik'].value_counts()
    st.bar_chart(sebaran_kategori, color="#4CAF50")


# 7. VISUALISASI BARIS KEDUA 
st.markdown("---")
st.subheader("🏢 Distribusi Beban Kerja (Top 10 Unit Pelaksana Terpadat)")
beban_pic = df_filtered['pic_pelaksana'].value_counts().head(10)
st.bar_chart(beban_pic, color="#2196F3")


# 8. TABEL RINCIAN
st.markdown("---")
st.subheader("📑 Detail Rencana Aksi")
with st.expander("Klik di sini untuk melihat/menyembunyikan tabel rincian data"):
    st.dataframe(df_filtered, use_container_width=True)

st.caption("Dikembangkan oleh Abdillah Fikri Alpome - Kerja Praktik BPS RI 2026")