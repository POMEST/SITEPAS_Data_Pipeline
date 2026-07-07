import pandas as pd
import os
import numpy as np

KATEGORI = 'Ketahanan Pangan Nasional'
NOMOR = '5'

print(f"Memulai proses ETL untuk {KATEGORI}...")
file_path = r'data\raw\Kompilasi Renaksi RB 2026 Hasil Penajaman Sekretariat.xlsx'

nama_sheet = 'RB Tematik 5. Pangan_'

try:
    df_tem = pd.read_excel(file_path, sheet_name=nama_sheet, skiprows=2)
except Exception as e:
    print(f"ERROR: Sheet '{nama_sheet}' tidak dapat dibaca. Pastikan nama sheet benar. Detail: {e}")
    exit()

# Mengubah nama kolom menjadi format index angka (col_0 sampai col_20)
df_tem.columns = [f'col_{i}' for i in range(len(df_tem.columns))]

# Menghapus baris index ke-0 (sub-header)
df_tem = df_tem.iloc[1:].reset_index(drop=True)

# Memetakan kolom berdasarkan struktur Excel Tematik 5 yang sebenarnya
df_bersih = pd.DataFrame({
    'pic_pelaksana': df_tem['col_0'],       
    'fokus_tematik': df_tem['col_2'],
    'catatan': df_tem['col_3'],             
    'rekomendasi': df_tem['col_4'],         
    'sasaran_tematik': df_tem['col_5'],     
    'intervensi': df_tem['col_6'],          
    'permasalahan': df_tem['col_7'],
    'rencana_aksi_desc': df_tem['col_8'],   # Nama Kegiatan
    'sasaran': df_tem['col_9'],             
    'indikator_kegiatan': df_tem['col_10'],
    'target_2026': df_tem['col_11'],
    'rencana_kerja': df_tem['col_12'],
    'output_satuan': df_tem['col_13'],      # Satuan
    'tw1': df_tem['col_15'],                # TW 1
    'tw2': df_tem['col_16'],                # TW 2
    'tw3': df_tem['col_17'],                # TW 3
    'tw4': df_tem['col_18'],                # TW 4
    'anggaran': df_tem['col_19'],           # Anggaran
    'pic_detail': df_tem['col_20']          # PIC (Jabatan; No WA) - Berakhir di indeks 20
})

# Tambal sel yang digabung (Merged Cells) dari atas ke bawah
kolom_induk = [
    'pic_pelaksana', 'fokus_tematik', 'catatan', 'rekomendasi', 
    'sasaran_tematik', 'intervensi', 'permasalahan'
]
for col in kolom_induk:
    df_bersih[col] = df_bersih[col].ffill()

# --- FILTER AJAIB PENGHAPUS JUNK DATA ---
df_bersih = df_bersih.dropna(subset=['rencana_aksi_desc'])
# ----------------------------------------

# Tambahkan label kategori
df_bersih['kategori'] = KATEGORI
df_bersih['indikator_utama'] = KATEGORI 

# --- Membuat Simulasi Capaian Persentase (0-100%) ---
np.random.seed(int(NOMOR)) 
df_bersih['capaian_persen'] = np.random.randint(10, 101, size=len(df_bersih))

# Simpan hasil olahan
path_simpan = rf'data\processed\master_tematik_{NOMOR}.csv'
os.makedirs(r'data\processed', exist_ok=True)
df_bersih.to_csv(path_simpan, index=False)

print(f"✅ Proses ETL Tematik {NOMOR} Selesai! File bersih dari Junk Data dan disimpan di {path_simpan}")