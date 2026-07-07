import pandas as pd
import os
import numpy as np

KATEGORI = 'Peningkatan Akses, Kualitas, dan Mutu Pendidikan'
NOMOR = '6'

print(f"Memulai proses ETL untuk {KATEGORI}...")
file_path = r'data\raw\Kompilasi Renaksi RB 2026 Hasil Penajaman Sekretariat.xlsx'

nama_sheet = 'RB Tematik 6. Pendidikan_'

try:
    df_tem = pd.read_excel(file_path, sheet_name=nama_sheet, skiprows=2)
except Exception as e:
    print(f"ERROR: Sheet '{nama_sheet}' tidak dapat dibaca. Pastikan nama sheet benar. Detail: {e}")
    exit()

# Mengubah nama kolom menjadi format index angka
df_tem.columns = [f'col_{i}' for i in range(len(df_tem.columns))]

# Menghapus baris index ke-0 (sub-header)
df_tem = df_tem.iloc[1:].reset_index(drop=True)

# Memetakan kolom dengan "Sabuk Pengaman" .get()
# Jika kolom tidak ada, akan otomatis diisi nilai kosong (tanpa error)
df_bersih = pd.DataFrame({
    'pic_pelaksana': df_tem.get('col_3'),       # Unit Kerja Eselon 2
    'fokus_tematik': df_tem.get('col_1'),       
    'permasalahan': df_tem.get('col_2'),
    'rencana_aksi_desc': df_tem.get('col_4'),   # Nama Kegiatan
    'sasaran': df_tem.get('col_5'),
    'indikator_kegiatan': df_tem.get('col_6'),
    'target_2026': df_tem.get('col_7'),
    'rencana_kerja': df_tem.get('col_8'),
    'output_satuan': df_tem.get('col_9'),
    'output_indikator': df_tem.get('col_10'),
    'tw1': df_tem.get('col_11'),
    'tw2': df_tem.get('col_12'),
    'tw3': df_tem.get('col_13'),
    'tw4': df_tem.get('col_14'),
    'anggaran': df_tem.get('col_15'),           # Digeser ke 15
    'pic_detail': df_tem.get('col_16')          # Digeser ke 16
})

# Tambal sel yang digabung (Merged Cells) dari atas ke bawah
kolom_induk = ['fokus_tematik', 'permasalahan', 'pic_pelaksana']
for col in kolom_induk:
    if col in df_bersih.columns:
        df_bersih[col] = df_bersih[col].ffill()

# --- FILTER AJAIB PENGHAPUS JUNK DATA ---
# Hanya menyimpan baris yang memiliki "Nama Kegiatan"
df_bersih = df_bersih.dropna(subset=['rencana_aksi_desc'])
# ----------------------------------------

# Tambahkan label kategori sebagai pengenal di Dashboard
df_bersih['kategori'] = KATEGORI
df_bersih['indikator_utama'] = KATEGORI 

# --- Membuat Simulasi Capaian Persentase (0-100%) ---
np.random.seed(int(NOMOR)) 
df_bersih['capaian_persen'] = np.random.randint(10, 101, size=len(df_bersih))

# Simpan hasil olahan ke dalam folder processed
path_simpan = rf'data\processed\master_tematik_{NOMOR}.csv'
os.makedirs(r'data\processed', exist_ok=True)
df_bersih.to_csv(path_simpan, index=False)

print(f"✅ Proses ETL Tematik {NOMOR} Selesai! File bersih dari Junk Data dan disimpan di {path_simpan}")