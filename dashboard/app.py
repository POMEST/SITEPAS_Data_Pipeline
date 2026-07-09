import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Dashboard Evaluasi RB 2025", layout="wide", page_icon="📈")

# --- CSS CUSTOM UNTUK MENINGKATKAN UI ---
st.markdown("""
<style>
    .metric-container {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data 
def load_data():
    def read_csv_safe(file_name):
        path = os.path.join('data', 'processed', file_name)
        if os.path.exists(path): return pd.read_csv(path)
        return pd.DataFrame()
    return read_csv_safe('master_general_2025.csv'), read_csv_safe('master_tematik_2025.csv'), read_csv_safe('master_tematik_baru_2025.csv')

df_gen, df_tem, df_tem_baru = load_data()

def tampilkan_scorecard(df_filter):
    st.markdown("### Ringkasan Eksekutif")
    c1, c2, c3 = st.columns(3)
    with c1: 
        st.markdown(f"<div class='metric-container'><h4>Total Rencana Aksi</h4><h2>{len(df_filter)}</h2></div>", unsafe_allow_html=True)
    with c2: 
        st.markdown(f"<div class='metric-container'><h4>Unit/PIC Terlibat</h4><h2>{df_filter['pic_pelaksana'].nunique()}</h2></div>", unsafe_allow_html=True)
    
    # Rata-rata dihitung dari yang memiliki status 'Tercapai', 'Tercapai Melebihi Target', 'Belum Tercapai Pada TW Ini' (Tidak termasuk yang Belum Ada Target)
    valid_rows = df_filter[df_filter['tw4_status'].isin(['Tercapai', 'Tercapai Melebihi Target', 'Belum Tercapai Pada TW Ini'])]
    if not valid_rows.empty:
        rata_capaian = valid_rows['tw4_capaian'].astype(float).mean()
        rata_text = f"{rata_capaian:.1f}%"
    else:
        rata_text = "N/A"
        
    with c3: 
        st.markdown(f"<div class='metric-container'><h4>Rata-rata Capaian (TW4)</h4><h2>{rata_text}</h2></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

def tampilkan_card_rencana_aksi(row, is_tematik_baru=False):
    with st.container(border=True):
        st.subheader(row['rencana_aksi_desc'])
        
        # Meta info
        col_meta1, col_meta2 = st.columns([1, 1])
        with col_meta1:
            st.caption(f"**PIC Pelaksana:** {row['pic_pelaksana']}")
        with col_meta2:
            st.caption(f"**Satuan Output:** {row['satuan']}")
            
        if is_tematik_baru and 'penyesuaian_tema' in row and pd.notna(row['penyesuaian_tema']):
            st.info(f"🔄 **Penyesuaian Tema:** {row['penyesuaian_tema']}")
            
        st.markdown("---")
        
        # Area Triwulan
        t_cols = st.columns(4)
        for tw in range(1, 5):
            with t_cols[tw-1]:
                st.markdown(f"**Triwulan {tw}**")
                status = str(row.get(f'tw{tw}_status', '-'))
                capaian = row.get(f'tw{tw}_capaian', 0.0)
                
                try: capaian_val = float(capaian)
                except: capaian_val = 0.0
                
                # RENDERING STATUS SESUAI LOGIKA BARU
                if status == "Belum Ada Target Pada TW Ini":
                    st.markdown("<p style='color: grey;'>⚪ <i>Belum ada target</i></p>", unsafe_allow_html=True)
                elif status == "Tercapai Lebih Awal":
                    st.success(f"⭐ **100%** (Selesai Lebih Awal)")
                elif status == "Tercapai":
                    st.metric(label="", value=f"{capaian_val:.0f}%", label_visibility="collapsed")
                    st.progress(1.0) # Bar penuh
                    st.caption("✅ Tercapai")
                elif status == "Tercapai Melebihi Target":
                    st.metric(label="", value=f"{capaian_val:.0f}%", label_visibility="collapsed")
                    st.progress(1.0) # Bar penuh
                    st.caption("🔥 Melebihi Target")
                elif status == "Belum Tercapai Pada TW Ini":
                    st.metric(label="", value=f"{capaian_val:.1f}%", label_visibility="collapsed")
                    st.progress(min(capaian_val / 100.0, 1.0))
                    st.caption("⚠️ Belum Tercapai")
                else:
                    st.markdown("-")
                    
        # --- KENDALA & SOLUSI ---
        kendala = str(row.get('tw4_kendala', '')).strip()
        solusi = str(row.get('tw4_solusi', '')).strip()
        
        # Tampilkan expander jika ada kendala/solusi (menghemat ruang UI)
        has_kendala = kendala.lower() not in ['nan', 'none', '-', '']
        has_solusi = solusi.lower() not in ['nan', 'none', '-', '']
        
        if has_kendala or has_solusi:
            with st.expander("Lihat Kendala & Solusi (TW 4)"):
                if has_kendala:
                    st.error(f"🚨 **Kendala:** {row['tw4_kendala']}")
                if has_solusi:
                    st.info(f"💡 **Solusi/Tindak Lanjut:** {row['tw4_solusi']}")

# --- MAIN APP LAYOUT ---
st.title("📈 Dashboard Evaluasi Kinerja RB BPS (Tahun 2025)")
st.markdown("Aplikasi Monitoring dan Perancangan Data Pipeline Rencana Aksi Reformasi Birokrasi.")
st.markdown("---")

tab_general, tab_tematik, tab_tematik_baru = st.tabs([
    "📊 EVALUASI RB GENERAL", 
    "🎯 EVALUASI RB TEMATIK", 
    "🚀 EVALUASI TEMATIK BARU"
])

# Render TAB GENERAL
with tab_general:
    if not df_gen.empty:
        indeks = st.selectbox("Pilih Indikator Utama (General):", options=df_gen['indikator_utama'].dropna().unique())
        df_filter = df_gen[df_gen['indikator_utama'] == indeks]
        tampilkan_scorecard(df_filter)
        for _, row in df_filter.iterrows(): 
            tampilkan_card_rencana_aksi(row)
    else:
        st.warning("Data RB General belum tersedia. Pastikan proses ETL telah dijalankan.")

# Render TAB TEMATIK
with tab_tematik:
    if not df_tem.empty:
        tema = st.selectbox("Pilih Fokus Tematik:", options=df_tem['indikator_utama'].dropna().unique())
        df_filter = df_tem[df_tem['indikator_utama'] == tema]
        tampilkan_scorecard(df_filter)
        for _, row in df_filter.iterrows(): 
            tampilkan_card_rencana_aksi(row)
    else:
        st.warning("Data RB Tematik belum tersedia. Pastikan proses ETL telah dijalankan.")

# Render TAB TEMATIK BARU
with tab_tematik_baru:
    if not df_tem_baru.empty:
        tema_baru = st.selectbox("Pilih Fokus Tematik Baru:", options=df_tem_baru['indikator_utama'].dropna().unique())
        df_filter = df_tem_baru[df_tem_baru['indikator_utama'] == tema_baru]
        tampilkan_scorecard(df_filter)
        for _, row in df_filter.iterrows(): 
            tampilkan_card_rencana_aksi(row, is_tematik_baru=True)
    else:
        st.warning("Data RB Tematik Baru belum tersedia. Pastikan proses ETL telah dijalankan.")