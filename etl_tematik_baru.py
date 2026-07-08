import pandas as pd
import os

print("Memulai proses ETL Faktual untuk Tematik Baru 2025...")
file_path = r'data\raw\Kertas Kerja Evaluasi On Going RB 2025_TW4.xlsx'

nama_sheet = 'Tematik Baru'

try:
    df_tem = pd.read_excel(file_path, sheet_name=nama_sheet, skiprows=2)
except ValueError:
    print(f"Error: Sheet '{nama_sheet}' tidak ditemukan.")
    exit()

df_tem.columns = [f'col_{i}' for i in range(len(df_tem.columns))]

df_bersih = pd.DataFrame({
    'indikator_utama': df_tem.get('col_1'),   # Tema
    'penyesuaian_tema': df_tem.get('col_2'),
    'rencana_aksi_desc': df_tem.get('col_9'), # Rencana Aksi (Lebih jauh ke kanan)
    'pic_pelaksana': df_tem.get('col_18'),    # Unit Pelaksana
    'anggaran': df_tem.get('col_17'),
    
    # Realisasi TW 1
    'tw1_capaian': df_tem.get('col_21'),
    'tw1_kendala': df_tem.get('col_23'),
    'tw1_solusi': df_tem.get('col_24'),
    
    # Realisasi TW 2
    'tw2_capaian': df_tem.get('col_26'),
    'tw2_kendala': df_tem.get('col_28'),
    'tw2_solusi': df_tem.get('col_29'),
    
    # Realisasi TW 3
    'tw3_capaian': df_tem.get('col_31'),
    'tw3_kendala': df_tem.get('col_33'),
    'tw3_solusi': df_tem.get('col_34'),
    
    # Realisasi TW 4
    'tw4_capaian': df_tem.get('col_36'),
    'tw4_kendala': df_tem.get('col_38'),
    'tw4_solusi': df_tem.get('col_39'),
})

if 'indikator_utama' in df_bersih.columns:
    df_bersih['indikator_utama'] = df_bersih['indikator_utama'].ffill()

df_bersih = df_bersih.dropna(subset=['rencana_aksi_desc'])

# Fungsi Pembersih Persentase
def clean_percentage(val):
    if pd.isna(val): return 0.0
    val_str = str(val).replace('%', '').strip()
    try: return float(val_str)
    except ValueError: return 0.0

for tw in ['tw1_capaian', 'tw2_capaian', 'tw3_capaian', 'tw4_capaian']:
    if tw in df_bersih.columns:
        df_bersih[tw] = df_bersih[tw].apply(clean_percentage)

df_bersih['capaian_tahunan_rata'] = df_bersih[['tw1_capaian', 'tw2_capaian', 'tw3_capaian', 'tw4_capaian']].mean(axis=1)
df_bersih['kategori_tab'] = 'Tematik Baru'

os.makedirs(r'data\processed', exist_ok=True)
path_simpan = r'data\processed\master_tematik_baru_2025.csv'
df_bersih.to_csv(path_simpan, index=False)

print(f"✅ ETL Tematik Baru 2025 Sukses! Data disimpan di {path_simpan}")