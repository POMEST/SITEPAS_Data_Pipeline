import pandas as pd
import os
import numpy as np

KATEGORI = 'Peningkatan Kualitas dan Akses Layanan Kesehatan'
NOMOR = '4'

print(f"Memulai proses ETL untuk {KATEGORI}...")
file_path = r'data\raw\Kompilasi Renaksi RB 2026 Hasil Penajaman Sekretariat.xlsx'

nama_sheet = 'RB Tematik 4. Kesehatan_'

try:
    df_tem = pd.read_excel(file_path, sheet_name=nama_sheet, skiprows=2)
except Exception as e:
    print(f"ERROR: Sheet '{nama_sheet}' tidak dapat dibaca. Pastikan nama sheet benar. Detail: {e}")
    exit()

# Mengubah nama kolom menjadi format index angka (col_0 sampai col_18)
df_tem.columns = [f'col_{i}' for i in range(len(df_tem.columns))]

# Menghapus baris index ke-0 (karena ini adalah sub-header: Satuan, Indikator, TW I, dll)
df_tem = df_tem.iloc[1:].reset_index(drop=True)

# Memetakan kolom berdasarkan struktur Excel Tematik 4 (Kesehatan)
# A=0, B=1, C=2, D=3, E=4, F=5, G=6, H=7, I=8, J=9, K=10, L=11, M=12, N=13, O=14, P=15, Q=16, R=17, S=18
df_bersih = pd.DataFrame({
    'pic_pelaksana': df_tem['col_0'],       # Unit Kerja Eselon 2 (Paling kiri)
    'fokus_tematik': df_tem['col_2'],
    'permasalahan': df_tem['col_3'],
    'rencana_aksi_desc': df_tem['col_4'],   # Nama Kegiatan
    'sasaran': df_tem['col_5'],
    'indikator_kegiatan': df_tem['col_6'],
    'target_2026': df_tem['col_7'],
    'rencana_kerja': df_tem['col_8'],
    'intervensi': df_tem['col_9'],          # Kolom spesifik di Tematik 4
    'output_satuan': df_tem['col_10'],
    'output_indikator': df_tem['col_11'],
    'tw1': df_tem['col_12'],
    'tw2': df_tem['col_13'],
    'tw3': df_tem['col_14'],
    'tw4': df_tem['col_15'],
    'anggaran': df_tem['col_16'],
    'pic_detail': df_tem['col_17'],         # PIC (Jabatan; No WA)
    'rekomendasi': df_tem['col_18']         # Kolom spesifik di Tematik 4
})

# Tambal sel yang digabung (Merged Cells) dari atas ke bawah
# Karena struktur rata kiri, kita menambal Unit Kerja, Fokus, dan Permasalahan
kolom_induk = ['pic_pelaksana', 'fokus_tematik', 'permasalahan']
for col in kolom_induk:
    df_bersih[col] = df_bersih[col].ffill()

# --- FILTER AJAIB PENGHAPUS JUNK DATA ---
# Membuang semua baris kosong atau catatan di luar tabel
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