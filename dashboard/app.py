import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Dashboard Evaluasi RB 2025", layout="wide", page_icon="📈")

# --- CUSTOM CSS ---
st.markdown("""
<style>
.metric-container {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 5px;
    padding: 15px;
    text-align: center;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
}
.metric-container h4 {
    margin-top: 0;
    color: #6c757d;
    font-size: 1rem;
}
.metric-container h2 {
    margin-bottom: 0;
    color: #343a40;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data 
def load_data():
    def read_csv_safe(file_name):
        path = os.path.join('data', 'processed', file_name)
        if os.path.exists(path): return pd.read_csv(path)
        return pd.DataFrame()
        
    # Pastikan nama file disesuaikan dengan file hasil cleaning yang terakhir dibuat
    return read_csv_safe('master_general_2025_cleaned.csv'), \
           read_csv_safe('master_tematik_2025_cleaned.csv'), \
           read_csv_safe('master_tematik_baru_2025_cleaned.csv')

df_gen, df_tem, df_tem_baru = load_data()


def tampilkan_scorecard(df_filter):
    st.markdown("### Ringkasan Eksekutif")
    c1, c2, c3 = st.columns(3)
    
    with c1: 
        st.markdown(f"<div class='metric-container'><h4>Total Rencana Aksi</h4><h2>{len(df_filter)}</h2></div>", unsafe_allow_html=True)
    with c2: 
        st.markdown(f"<div class='metric-container'><h4>Unit/PIC Terlibat</h4><h2>{df_filter['pic_pelaksana'].nunique()}</h2></div>", unsafe_allow_html=True)
    
    # Menghitung Rata-rata dari kolom 'Persentase Pencapaian Target'
    if not df_filter.empty and 'Persentase Pencapaian Target' in df_filter.columns:
        # Menghapus simbol '%' dan mengubah ke numerik untuk dihitung rata-ratanya
        rata_capaian = df_filter['Persentase Pencapaian Target'].astype(str).str.replace('%', '').astype(float).mean()
        rata_text = f"{rata_capaian:.1f}%"
    else:
        rata_text = "N/A"
        
    with c3: 
        st.markdown(f"<div class='metric-container'><h4>Rata-rata Kelulusan Aksi</h4><h2>{rata_text}</h2></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


def tampilkan_card_rencana_aksi(row):
    with st.container(border=True):
        st.subheader(row.get('Rencana Aksi', 'Nama Rencana Aksi Tidak Ditemukan'))
        
        # Meta info
        col_meta1, col_meta2, col_meta3 = st.columns([2, 1, 1])
        with col_meta1:
            st.caption(f"**PIC Pelaksana:** {row.get('pic_pelaksana', '-')}")
        with col_meta2:
            st.caption(f"**Satuan Output:** {row.get('output(Satuan)', '-')}")
        with col_meta3:
            # Menampilkan Persentase Total Keseluruhan TW
            pct_total = row.get('Persentase Pencapaian Target', '0%')
            st.markdown(f"**Pencapaian Target:** :blue[{pct_total}]")
            
        st.markdown("---")
        
        # Area Triwulan
        t_cols = st.columns(4)
        for tw in range(1, 5):
            with t_cols[tw-1]:
                st.markdown(f"**Triwulan {tw}**")
                
                # Mengambil nilai capaian dan target
                capaian = row.get(f'capaian output tw {tw}', 0.0)
                target = row.get(f'target tw {tw}', 0.0)
                status = str(row.get(f'status tw {tw}', '-'))
                
                # Format angka untuk menghilangkan desimal .0 jika memungkinkan
                def format_num(val):
                    try: return f"{float(val):.0f}" if float(val).is_integer() else f"{float(val)}"
                    except: return str(val)
                
                st.caption(f"Capaian: **{format_num(capaian)}** / Target: **{format_num(target)}**")
                
                # Logika Simbol Centang dan Silang
                if status == "Target Tercapai":
                    st.success("✅ Target Tercapai")
                elif status == "Tidak Ada Target":
                    st.info("✅ Aman (Tidak Ada Target)")
                elif status == "Tidak Tercapai":
                    st.error("❌ Tidak Tercapai")
                else:
                    st.markdown("-")


# --- MAIN APP LAYOUT ---
st.title("📈 Dashboard Evaluasi Kinerja RB BPS (Tahun 2025)")
st.markdown("Aplikasi Monitoring dan Evaluasi Pencapaian Target per Rencana Aksi.")
st.markdown("---")

tab_general, tab_tematik, tab_tematik_baru = st.tabs([
    "📊 EVALUASI RB GENERAL", 
    "🎯 EVALUASI RB TEMATIK", 
    "🚀 EVALUASI TEMATIK BARU"
])

# Render TAB GENERAL    
with tab_general:
    if not df_gen.empty:
        indeks = st.selectbox("Pilih Indikator Utama (General):", options=df_gen['indikator kegiatan utama'].dropna().unique())
        df_filter = df_gen[df_gen['indikator kegiatan utama'] == indeks]
        tampilkan_scorecard(df_filter)
        for _, row in df_filter.iterrows(): 
            tampilkan_card_rencana_aksi(row)
    else:
        st.warning("Data RB General belum tersedia. Pastikan file CSV tersedia di folder data/processed.")

# Render TAB TEMATIK
with tab_tematik:
    if not df_tem.empty:
        tema = st.selectbox("Pilih Fokus Tematik:", options=df_tem['indikator kegiatan utama'].dropna().unique())
        df_filter = df_tem[df_tem['indikator kegiatan utama'] == tema]
        tampilkan_scorecard(df_filter)
        for _, row in df_filter.iterrows(): 
            tampilkan_card_rencana_aksi(row)
    else:
        st.warning("Data RB Tematik belum tersedia. Pastikan file CSV tersedia di folder data/processed.")

# Render TAB TEMATIK BARU
with tab_tematik_baru:
    if not df_tem_baru.empty:
        tema_baru = st.selectbox("Pilih Fokus Tematik Baru:", options=df_tem_baru['indikator kegiatan utama'].dropna().unique())
        df_filter = df_tem_baru[df_tem_baru['indikator kegiatan utama'] == tema_baru]
        tampilkan_scorecard(df_filter)
        for _, row in df_filter.iterrows(): 
            tampilkan_card_rencana_aksi(row)
    else:
        st.warning("Data RB Tematik Baru belum tersedia. Pastikan file CSV tersedia di folder data/processed.")