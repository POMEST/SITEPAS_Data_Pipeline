import pandas as pd
import os

print("Memulai proses ETL Faktual untuk Dashboard RB General 2025...")
# Sesuaikan kembali path Anda jika di perlukan
file_path = r'data\raw\Kertas Kerja Evaluasi On Going RB 2025_TW4.xlsx'

# 1. Ekstraksi Data (Sesuai dengan mapping letak kolom Sheet General)
df_raw = pd.read_excel(file_path, sheet_name='General', header=None)
df_data = df_raw.iloc[5:].reset_index(drop=True)

df_bersih = pd.DataFrame({
    'kegiatan_utama': df_data[1].ffill(),
    'indikator_kegiatan_utama': df_data[2].ffill(),
    'rencana_aksi': df_data[5],
    'output_satuan': df_data[6],
    'pic_pelaksana': df_data[14], # Diambil dari Kolom "Koordinator (PJK)"
    
    'tw1_target_raw': df_data[8],
    'tw2_target_raw': df_data[9],
    'tw3_target_raw': df_data[10],
    'tw4_target_raw': df_data[11],
    
    'tw1_capaian_raw': df_data[17],
    'tw2_capaian_raw': df_data[23],
    'tw3_capaian_raw': df_data[29],
    'tw4_capaian_raw': df_data[35],
})

# Hilangkan data yang kosong atau cuma berisi header berulang
df_bersih = df_bersih.dropna(subset=['rencana_aksi'])
df_bersih = df_bersih[~df_bersih['rencana_aksi'].astype(str).str.contains('Rencana Aksi', case=False)]


# 2. Fungsi Ekstrak Angka Target
def parse_target(val):
    if pd.isna(val): return 0.0
    s = str(val).strip().lower()
    if s in ['-', '', 'nan', 'none']: return 0.0
    
    s = s.replace('%', '').replace(',', '.')
    try:
        return float(s)
    except ValueError:
        return 0.0

# 3. Fungsi Ekstrak Capaian (Dengan Fallback ke Target Jika Berisi Teks)
def parse_capaian(val, target_val):
    if pd.isna(val): return 0.0
    s = str(val).strip().lower()
    if s in ['-', '', 'nan', 'none']: return 0.0
    
    s = s.replace('%', '').replace(',', '.')
    try:
        return float(s)
    except ValueError:
        # Jika nilai error diubah jadi angka (karena teks/huruf), kembalikan nilai target TW-nya
        return float(target_val)


# 4. Proses Transformasi Logika Khusus
tw1_t, tw2_t, tw3_t, tw4_t = [], [], [], []
tw1_c, tw2_c, tw3_c, tw4_c = [], [], [], []

for idx, row in df_bersih.iterrows():
    # Parsing Dasar
    t1 = parse_target(row['tw1_target_raw'])
    t2 = parse_target(row['tw2_target_raw'])
    t3 = parse_target(row['tw3_target_raw'])
    t4 = parse_target(row['tw4_target_raw'])
    
    # Parsing capaian, berikan argumen target masing-masing TW sebagai penolong jika isi text
    c1 = parse_capaian(row['tw1_capaian_raw'], t1)
    c2 = parse_capaian(row['tw2_capaian_raw'], t2)
    c3 = parse_capaian(row['tw3_capaian_raw'], t3)
    c4 = parse_capaian(row['tw4_capaian_raw'], t4)
    
    # ATURAN: Jika target TW 4 adalah 100, normalkan semuanya menjadi Persen Desimal
    if t4 == 100.0:
        t1 = t1 / 100.0 if t1 > 1.0 else t1
        t2 = t2 / 100.0 if t2 > 1.0 else t2
        t3 = t3 / 100.0 if t3 > 1.0 else t3
        t4 = 1.0 # 100 menjadi 1.0 (100%)
        
        # Normalkan juga nilai capaian agar visualisasi Streamlit konsisten
        c1 = c1 / 100.0 if c1 > 1.0 else c1
        c2 = c2 / 100.0 if c2 > 1.0 else c2
        c3 = c3 / 100.0 if c3 > 1.0 else c3
        c4 = c4 / 100.0 if c4 > 1.0 else c4
        
    tw1_t.append(t1); tw2_t.append(t2); tw3_t.append(t3); tw4_t.append(t4)
    tw1_c.append(c1); tw2_c.append(c2); tw3_c.append(c3); tw4_c.append(c4)


# 5. Gabungkan menjadi DataFrame baru yang sesuai pesanan
df_final = pd.DataFrame({
    'kegiatan_utama': df_bersih['kegiatan_utama'],
    'indikator_kegiatan_utama': df_bersih['indikator_kegiatan_utama'],
    'rencana_aksi': df_bersih['rencana_aksi'],
    'output_satuan': df_bersih['output_satuan'],
    'pic_pelaksana': df_bersih['pic_pelaksana'],
    'target_tw_1': tw1_t,
    'target_tw_2': tw2_t,
    'target_tw_3': tw3_t,
    'target_tw_4': tw4_t,
    'capaian_output_tw_1': tw1_c,
    'capaian_output_tw_2': tw2_c,
    'capaian_output_tw_3': tw3_c,
    'capaian_output_tw_4': tw4_c,
})

# 6. Simpan CSV
os.makedirs(r'data\processed', exist_ok=True)
output_file = r'data\processed\master_general_dashboard.csv'
df_final.to_csv(output_file, index=False)

print(f"✅ ETL Sukses! Data siap digunakan di Streamlit. Cek folder {output_file}")