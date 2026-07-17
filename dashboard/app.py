import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
import plotly.express as px
from kmeans_processor import jalankan_kmeans  # Mengimpor fungsi K-Means


st.set_page_config(page_title="Dashboard Evaluasi RB 2025", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
.metric-container {
    background-color: #222831;
    border: 1px solid #31363F;
    border-radius: 5px;
    padding: 15px;
    text-align: center;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
}
.metric-container h4 {
    margin-top: 0;
    color: #ffffff;
    font-size: 1rem;
}
.metric-container h2 {
    margin-bottom: 0;
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data 
def load_data():
    def read_csv_safe(file_name):
        path = os.path.join('data', 'processed', file_name)
        # Menyesuaikan path jika script dijalankan dari direktori yang berbeda
        if not os.path.exists(path):
            path = file_name
            
        if os.path.exists(path): 
            return pd.read_csv(path)
        return pd.DataFrame()
        
    return read_csv_safe('master_general_2025_cleaned.csv'), \
           read_csv_safe('master_tematik_2025_cleaned.csv'), \
           read_csv_safe('master_tematik_baru_2025_cleaned.csv')

df_gen, df_tem, df_tem_baru = load_data()


# ==========================================
# FUNGSI: TAMPILAN OVERVIEW KESELURUHAN
# ==========================================
def tampilkan_overview_umum(df, judul_tab):
    st.markdown(f"## Tinjauan Umum: {judul_tab}")
    st.caption("Ringkasan performa dari seluruh indikator utama sebelum difilter.")
    
    # 1. Metrik Agregat Keseluruhan
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label="Total Seluruh Rencana Aksi", value=len(df))
    with c2:
        if 'indikator kegiatan utama' in df.columns:
            st.metric(label="Total Indikator Utama", value=df['indikator kegiatan utama'].nunique())
        else:
            st.metric(label="Total Indikator Utama", value="N/A")
    with c3:
        if 'pic_pelaksana' in df.columns:
            st.metric(label="Total PIC Terlibat", value=df['pic_pelaksana'].nunique())
        else:
            st.metric(label="Total PIC Terlibat", value="N/A")
    with c4:
        if 'Persentase Pencapaian Target' in df.columns:
            rata_all = df['Persentase Pencapaian Target'].astype(str).str.replace('%', '').astype(float).mean()
            st.metric(label="Rata-rata Capaian (Total)", value=f"{rata_all:.1f}%")
        else:
            st.metric(label="Rata-rata Capaian (Total)", value="N/A")
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_chart, col_insight = st.columns([2, 1])
    
    # 2. Visualisasi Data (Plotly Chart)
    with col_chart:
        st.markdown("**Sebaran Status Akhir (TW 4) per Indikator Utama**")
        if 'status tw 4' in df.columns and 'indikator kegiatan utama' in df.columns:
            # Mengelompokkan data untuk chart
            df_chart = df.groupby(['indikator kegiatan utama', 'status tw 4']).size().reset_index(name='Jumlah Aksi')
            
            # Menyingkat teks indikator yang terlalu panjang agar chart tidak rusak
            df_chart['Indikator (Pendek)'] = df_chart['indikator kegiatan utama'].apply(
                lambda x: str(x)[:40] + '...' if len(str(x)) > 40 else str(x)
            )
            
            fig = px.bar(
                df_chart, 
                x='Indikator (Pendek)', 
                y='Jumlah Aksi', 
                color='status tw 4',
                color_discrete_map={
                    "Target Tercapai": "#28a745",   # Hijau
                    "Tidak Ada Target": "#17a2b8",  # Biru (Aman)
                    "Tidak Tercapai": "#dc3545"     # Merah
                }
            )
            
            fig.update_layout(
                xaxis_title="", 
                yaxis_title="Jumlah Rencana Aksi", 
                legend_title="Status (TW 4)",
                margin=dict(l=0, r=0, t=30, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
            
    # 3. Insight Tambahan
    with col_insight:
        st.markdown("**Insight Penting**")
        with st.container(border=True):
            # PIC dengan beban kerja terbanyak
            if 'pic_pelaksana' in df.columns:
                top_pic = df['pic_pelaksana'].value_counts().head(1)
                if not top_pic.empty:
                    st.write("**PIC Beban Kerja Tertinggi:**")
                    st.info(f"{top_pic.index[0]} ({top_pic.values[0]} Aksi)")
            
            # Mencari Rencana Aksi yang masih 0% capaiannya secara keseluruhan
            if 'Persentase Pencapaian Target' in df.columns:
                df_temp = df.copy()
                df_temp['pct_num'] = df_temp['Persentase Pencapaian Target'].astype(str).str.replace('%', '').astype(float)
                aksi_nol = df_temp[df_temp['pct_num'] == 0]
                st.write("**Aksi Belum Berjalan (0%):**")
                if not aksi_nol.empty:
                    st.error(f"Terdapat {len(aksi_nol)} Rencana Aksi yang capaiannya masih 0%.")
                else:
                    st.success("Seluruh Rencana Aksi memiliki progres positif!")

    st.divider()


# ==========================================
# FUNGSI BARU: VISUALISASI K-MEANS CLUSTERING
# ==========================================
def tampilkan_analisis_klaster(df):
    st.markdown("### 🤖 Analisis Segmentasi Kinerja (AI Clustering)")
    st.caption("Machine Learning mengelompokkan Rencana Aksi berdasarkan kemiripan pola eksekusi target dan capaian.")
    
    # Jalankan proses K-Means
    df_klaster = jalankan_kmeans(df, n_clusters=4)
    
    if 'Label_Klaster' not in df_klaster.columns:
        st.warning("Data tidak cukup untuk dilakukan klasterisasi oleh algoritma K-Means.")
        st.divider()
        return

    col1, col2 = st.columns([2, 1])
    
    with col1:
        # --- PERBAIKAN: Paksa kolom target & capaian menjadi tipe data numerik ---
        kolom_tw = [
            'target tw 1', 'target tw 2', 'target tw 3', 'target tw 4',
            'capaian output tw 1', 'capaian output tw 2', 'capaian output tw 3', 'capaian output tw 4'
        ]
        for col in kolom_tw:
            if col in df_klaster.columns:
                df_klaster[col] = pd.to_numeric(df_klaster[col], errors='coerce').fillna(0)
        # ------------------------------------------------------------------------

        # Menyiapkan kolom numerik untuk sumbu X dan Y pada Scatter Plot
        df_klaster['Total Target'] = df_klaster[['target tw 1', 'target tw 2', 'target tw 3', 'target tw 4']].sum(axis=1)
        df_klaster['Total Capaian'] = df_klaster[['capaian output tw 1', 'capaian output tw 2', 'capaian output tw 3', 'capaian output tw 4']].sum(axis=1)
        
        # Kolom hover data
        hover_cols = ['Rencana Aksi']
        if 'pic_pelaksana' in df_klaster.columns:
            hover_cols.append('pic_pelaksana')
            
        fig = px.scatter(
            df_klaster, 
            x='Total Target', 
            y='Total Capaian', 
            color='Label_Klaster',
            hover_data=hover_cols,
            title="Sebaran Karakteristik Rencana Aksi",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        # Tambahkan garis ideal (Target = Capaian)
        max_val = max(df_klaster['Total Target'].max(), df_klaster['Total Capaian'].max())
        if pd.isna(max_val) or max_val == 0: max_val = 10
        
        fig.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val,
                      line=dict(color="White", dash="dot"))
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.markdown("**Distribusi Klaster**")
        distribusi = df_klaster['Label_Klaster'].value_counts().reset_index()
        distribusi.columns = ['Klaster', 'Jumlah Aksi']
        st.dataframe(distribusi, use_container_width=True, hide_index=True)
        
        st.info("💡 **Insight:** Garis putus-putus menunjukkan rasio ideal di mana Total Capaian sama dengan Total Target. Algoritma mengelompokkan data berdasarkan seberapa jauh atau dekat kinerja mereka dari rasio ideal dan pola cicilan tiap triwulannya.")
    
    st.divider()


# ==========================================
# FUNGSI DETAIL PER INDIKATOR
# ==========================================
def tampilkan_scorecard(df_filter):
    st.markdown("### Detail Indikator Terpilih")
    c1, c2, c3 = st.columns(3)
    
    with c1: 
        st.markdown(f"<div class='metric-container'><h4>Rencana Aksi Spesifik</h4><h2>{len(df_filter)}</h2></div>", unsafe_allow_html=True)
    with c2:
        if 'pic_pelaksana' in df_filter.columns:
            st.markdown(f"<div class='metric-container'><h4>Unit/PIC Terlibat</h4><h2>{df_filter['pic_pelaksana'].nunique()}</h2></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='metric-container'><h4>Unit/PIC Terlibat</h4><h2>-</h2></div>", unsafe_allow_html=True)
            
    if not df_filter.empty and 'Persentase Pencapaian Target' in df_filter.columns:
        rata_capaian = df_filter['Persentase Pencapaian Target'].astype(str).str.replace('%', '').astype(float).mean()
        rata_text = f"{rata_capaian:.1f}%"
    else:
        rata_text = "N/A"
        
    with c3: 
        st.markdown(f"<div class='metric-container'><h4>Rata-rata Kelulusan</h4><h2>{rata_text}</h2></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


def tampilkan_card_rencana_aksi(row):
    with st.container(border=True):
        st.subheader(row.get('Rencana Aksi', 'Nama Rencana Aksi Tidak Ditemukan'))
        
        col_meta1, col_meta2, col_meta3 = st.columns([2, 1, 1])
        with col_meta1:
            st.caption(f"**PIC Pelaksana:** {row.get('pic_pelaksana', '-')}")
        with col_meta2:
            st.caption(f"**Satuan Output:** {row.get('output(Satuan)', '-')}")
        with col_meta3:
            pct_total = row.get('Persentase Pencapaian Target', '0%')
            st.markdown(f"**Pencapaian Target:** :blue[{pct_total}]")
            
        st.markdown("---")
        
        t_cols = st.columns(4)
        for tw in range(1, 5):
            with t_cols[tw-1]:
                st.markdown(f"**Triwulan {tw}**")
                
                capaian = row.get(f'capaian output tw {tw}', 0.0)
                target = row.get(f'target tw {tw}', 0.0)
                status = str(row.get(f'status tw {tw}', '-'))
                
                def format_num(val):
                    try: return f"{float(val):.0f}" if float(val).is_integer() else f"{float(val)}"
                    except: return str(val)
                
                st.caption(f"Capaian: **{format_num(capaian)}** / Target: **{format_num(target)}**")
                
                if status == "Target Tercapai":
                    st.success("✅ Target Tercapai")
                elif status == "Tidak Ada Target":
                    st.info("✅ Aman (Tidak Ada Target)")
                elif status == "Tidak Tercapai":
                    st.error("❌ Tidak Tercapai")
                else:
                    st.markdown("-")




# --- MAIN APP LAYOUT ---
st.title("Dashboard Evaluasi Kinerja RB BPS (Tahun 2025)")
st.markdown("Aplikasi Monitoring dan Evaluasi Pencapaian Target per Rencana Aksi.")
st.markdown("---")

tab_general, tab_tematik, tab_tematik_baru = st.tabs([
    "EVALUASI RB GENERAL", 
    "EVALUASI RB TEMATIK", 
    "EVALUASI TEMATIK BARU"
])

# Render TAB GENERAL    
with tab_general:
    if not df_gen.empty:
        tampilkan_overview_umum(df_gen, "RB General")
        tampilkan_analisis_klaster(df_gen) # Memanggil Visualisasi K-Means
        
        if 'indikator kegiatan utama' in df_gen.columns:
            indeks = st.selectbox("Pilih Indikator Utama (General) untuk Detail:", options=df_gen['indikator kegiatan utama'].dropna().unique())
            df_filter = df_gen[df_gen['indikator kegiatan utama'] == indeks]
            tampilkan_scorecard(df_filter)
            for _, row in df_filter.iterrows(): 
                tampilkan_card_rencana_aksi(row)
    else:
        st.warning("Data RB General belum tersedia atau format data tidak sesuai.")

# Render TAB TEMATIK
with tab_tematik:
    if not df_tem.empty:
        tampilkan_overview_umum(df_tem, "RB Tematik")
        tampilkan_analisis_klaster(df_tem) # Memanggil Visualisasi K-Means
        
        if 'indikator kegiatan utama' in df_tem.columns:
            tema = st.selectbox("Pilih Fokus Tematik untuk Detail:", options=df_tem['indikator kegiatan utama'].dropna().unique())
            df_filter = df_tem[df_tem['indikator kegiatan utama'] == tema]
            tampilkan_scorecard(df_filter)
            for _, row in df_filter.iterrows(): 
                tampilkan_card_rencana_aksi(row)
    else:
        st.warning("Data RB Tematik belum tersedia atau format data tidak sesuai.")

# Render TAB TEMATIK BARU
with tab_tematik_baru:
    if not df_tem_baru.empty:
        tampilkan_overview_umum(df_tem_baru, "RB Tematik Baru")
        tampilkan_analisis_klaster(df_tem_baru) # Memanggil Visualisasi K-Means
        
        if 'indikator kegiatan utama' in df_tem_baru.columns:
            tema_baru = st.selectbox("Pilih Fokus Tematik Baru untuk Detail:", options=df_tem_baru['indikator kegiatan utama'].dropna().unique())
            df_filter = df_tem_baru[df_tem_baru['indikator kegiatan utama'] == tema_baru]
            tampilkan_scorecard(df_filter)
            for _, row in df_filter.iterrows(): 
                tampilkan_card_rencana_aksi(row)
    else:
        st.warning("Data RB Tematik Baru belum tersedia atau format data tidak sesuai.")