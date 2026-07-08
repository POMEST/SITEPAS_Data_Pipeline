import pandas as pd
import os

print("Memulai proses ETL Faktual untuk RB General 2025...")
file_path = r'data\raw\Kertas Kerja Evaluasi On Going RB 2025_TW4.xlsx'

# Membaca data sheet 'General' (skip 2 baris header atas)
df_gen = pd.read_excel(file_path, sheet_name='General', skiprows=2)

# Menstandarkan nama kolom menggunakan indeks angka agar aman dari perubahan format
df_gen.columns = [f'col_{i}' for i in range(len(df_gen.columns))]

# Memetakan data sesuai struktur asli Kertas Kerja 2025
df_bersih = pd.DataFrame({
    'indikator_utama': df_gen['col_1'],       # Kegiatan Utama / Indeks
    'indikator_kegiatan': df_gen['col_2'],    # Indikator Kegiatan Utama
    'rencana_aksi_desc': df_gen['col_5'],     # Rencana Aksi
    'output_desc': df_gen['col_6'],           # Output
    'pic_pelaksana': df_gen['col_14'],        # Pelaksana (Unit/Satker)
    
    # Realisasi Progres Capaian Kualitatif & Kuantitatif 2025 per Triwulan
    'tw1_kegiatan': df_gen['col_15'],
    'tw1_capaian': df_gen['col_16'],
    'tw1_kendala': df_gen['col_18'],
    'tw1_solusi': df_gen['col_19'],
    
    'tw2_kegiatan': df_gen['col_21'],
    'tw2_capaian': df_gen['col_22'],
    'tw2_kendala': df_gen['col_24'],
    'tw2_solusi': df_gen['col_25'],
    
    'tw3_kegiatan': df_gen['col_27'],
    'tw3_capaian': df_gen['col_28'],
    'tw3_kendala': df_gen['col_30'],
    'tw3_solusi': df_gen['col_31'],
    
    'tw4_kegiatan': df_gen['col_33'],
    'tw4_capaian': df_gen['col_34'],
    'tw4_kendala': df_gen['col_36'],
    'tw4_solusi': df_gen['col_37'],
    
    # Catatan Evaluator
    'catatan_evaluatur_tw4': df_gen['col_40'] if 'col_40' in df_gen.columns else None
})

# Tambal Merged Cells untuk kolom Indikator Utama
df_bersih['indikator_utama'] = df_bersih['indikator_utama'].ffill()
df_bersih['indikator_kegiatan'] = df_bersih['indikator_kegiatan'].ffill()

# Bersihkan baris sampah (potong baris yang tidak memiliki deskripsi Rencana Aksi)
df_bersih = df_bersih.dropna(subset=['rencana_aksi_desc'])

# Membersihkan teks spasi tersembunyi
df_bersih['indikator_utama'] = df_bersih['indikator_utama'].str.strip()

# --- STANDARISASI ANGKA CAPAIAN (Mengubah Teks/Persen menjadi Angka Murni) ---
def clean_percentage(val):
    if pd.isna(val):
        return 0.0
    val_str = str(val).replace('%', '').strip()
    try:
        # Jika isinya angka biasa seperti 100 atau 85.5
        return float(val_str)
    except ValueError:
        # Jika isinya teks penjelasan (misal: "Belum terjadwal"), set ke 0 sementara
        return 0.0

# Bersihkan kolom capaian dari TW1 sampai TW4
for tw in ['tw1_capaian', 'tw2_capaian', 'tw3_capaian', 'tw4_capaian']:
    df_bersih[tw] = df_bersih[tw].apply(clean_percentage)

# Membuat nilai rata-rata kumulatif tahunan sebagai metrik utama di dashboard
df_bersih['capaian_tahunan_rata'] = df_bersih[['tw1_capaian', 'tw2_capaian', 'tw3_capaian', 'tw4_capaian']].mean(axis=1)

# Simpan ke folder processed
os.makedirs(r'data\processed', exist_ok=True)
path_simpan = r'data\processed\master_general_2025.csv'
df_bersih.to_csv(path_simpan, index=False)

print(f"✅ ETL General 2025 Sukses! Data FAKTUAL disimpan di {path_simpan}")