import pandas as pd
import os
import numpy as np

KATEGORI = 'Mendorong Hilirisasi'
NOMOR = '3'

print(f"Memulai proses ETL untuk {KATEGORI}...")
file_path = r'data\raw\Kompilasi Renaksi RB 2026 Hasil Penajaman Sekretariat.xlsx'

nama_sheet = 'RB Tematik 3. Hilirisasi_'

try:
    df_tem = pd.read_excel(file_path, sheet_name=nama_sheet, skiprows=2)
except Exception as e:
    print(f"ERROR: Sheet '{nama_sheet}' tidak dapat dibaca. Pastikan nama sheet benar. Detail: {e}")
    exit()

# Mengubah nama kolom menjadi format index angka
df_tem.columns = [f'col_{i}' for i in range(len(df_tem.columns))]

# Menghapus baris index ke-0 (karena ini adalah sub-header: Satuan, Indikator, TW I, dll)
df_tem = df_tem.iloc[1:].reset_index(drop=True)

# Memetakan kolom berdasarkan struktur Excel Tematik 3 (Hilirisasi)
# Karena ada kolom "Kemenpan RB", "Tema", "Intervensi", maka "Unit Kerja" bergeser ke col_6
try:
    df_bersih = pd.DataFrame({
        'pic_pelaksana': df_tem['col_6'],       # Unit Kerja Eselon 2
        'fokus_tematik': df_tem['col_8'],
        'permasalahan': df_tem['col_9'],
        'rencana_aksi_desc': df_tem['col_10'],  # Nama Kegiatan
        'sasaran': df_tem['col_11'],
        'indikator_kegiatan': df_tem['col_12'],
        'target_2026': df_tem['col_13'],
        'rencana_kerja': df_tem['col_14']
    })
except KeyError:
    # Sabuk pengaman jika indeks bergeser 1 angka akibat merged cells
    df_bersih = pd.DataFrame({
        'pic_pelaksana': df_tem['col_5'],       
        'fokus_tematik': df_tem['col_7'],
        'permasalahan': df_tem['col_8'],
        'rencana_aksi_desc': df_tem['col_9'],  
        'sasaran': df_tem['col_10'],
        'indikator_kegiatan': df_tem['col_11'],
        'target_2026': df_tem['col_12'],
        'rencana_kerja': df_tem['col_13']
    })

# Menambal sel yang digabung (Merged Cells) dari atas ke bawah
kolom_induk = ['pic_pelaksana', 'fokus_tematik', 'permasalahan', 'sasaran']
for col in kolom_induk:
    df_bersih[col] = df_bersih[col].ffill()

# --- JURUS PAMUNGKAS (Mengatasi 2 Tabel Berbeda) ---
# Membuang semua baris aneh / header tabel kedua yang bukan merupakan "Nama Kegiatan"
df_bersih = df_bersih.dropna(subset=['rencana_aksi_desc'])
# ---------------------------------------------------

# Tambahkan label kategori
df_bersih['kategori'] = KATEGORI
df_bersih['indikator_utama'] = KATEGORI 

# Membuat Simulasi Capaian Persentase (0-100%)
np.random.seed(int(NOMOR)) 
df_bersih['capaian_persen'] = np.random.randint(10, 101, size=len(df_bersih))

# Simpan hasil olahan ke dalam folder processed
path_simpan = rf'data\processed\master_tematik_{NOMOR}.csv'
os.makedirs(r'data\processed', exist_ok=True)
df_bersih.to_csv(path_simpan, index=False)

print(f"✅ Proses ETL Tematik {NOMOR} Selesai! File bersih dari Junk Data dan disimpan di {path_simpan}")