import pandas as pd
import os
import numpy as np

print("Memulai proses ETL untuk RB General...")
file_path = r'data\raw\Kompilasi Renaksi RB 2026 Hasil Penajaman Sekretariat.xlsx'

df_gen = pd.read_excel(file_path, sheet_name='RB General', skiprows=2)

df_gen.columns = [f'col_{i}' for i in range(len(df_gen.columns))]

df_bersih = pd.DataFrame({
    'indikator_utama': df_gen['col_1'],
    'rencana_aksi_desc': df_gen['col_5'],
    'pic_pelaksana': df_gen['col_15'], # Sesuaikan indeks kolom PIC jika perlu
    'target_2026': df_gen['col_3'],
})

df_bersih['indikator_utama'] = df_bersih['indikator_utama'].ffill()
df_bersih = df_bersih.dropna(subset=['rencana_aksi_desc'])
df_bersih['kategori'] = 'RB General'

urutan_index = [
    "Nilai SAKIP", "Capaian IKU Kementerian/Lembaga", "Penguatan Implementasi SPIP",
    "Capaian Prioritas Nasional", "Indeks Perencanaan Pembangunan", "Indeks Kualitas Kebijakan",
    "Indeks Reformasi Hukum", "Tingkat Capaian Sistem Kerja untuk Penyederhaan Birokrasi",
    "Persentase Penyederhaan Struktur Organisasi", "Tingkat Digitalisasi Arsip", 
    "Indeks Tata Kelola Pengadaan (ITKP)", "Indikator Kinerja Pelaksanaan Anggaran (IKPA)",
    "Opini BPK", "Indeks Pengelolaan Aset (IPA)", "Indeks BerAKHLAK", "Indeks Sistem Merit",
    "Indeks Pelayanan Publik (IPP)", "Tingkat Kepatuhan Standar Pelayanan Publik",
    "Survei Kepuasan Masyarakat", "Indeks Pembangunan Statistik", "Indeks SPBE / Pemerintah Digital",
    "Tingkat Implementasi Kebijakan Arsitektur SPBE", "Tindak Lanjut Rekomendasi",
    "Evaluasi Pembangunan Zona Integritas (ZI)", 
    "Tingkat tindak lanjut pengaduan masyarakat (LAPOR) yang sudah diselesaikan",
    "Survei Penilaian Integritas"
]

df_bersih['indikator_utama'] = df_bersih['indikator_utama'].str.strip()
urutan_index_bersih = [x.strip() for x in urutan_index]

df_bersih['indikator_utama'] = pd.Categorical(df_bersih['indikator_utama'], categories=urutan_index_bersih, ordered=True)
df_bersih = df_bersih.sort_values('indikator_utama').reset_index(drop=True)

np.random.seed(42)
df_bersih['capaian_persen'] = np.random.randint(15, 101, size=len(df_bersih))

os.makedirs(r'data\processed', exist_ok=True)
df_bersih.to_csv(r'data\processed\master_general.csv', index=False)
print("✅ Proses ETL General Selesai dengan urutan Indeks yang rapi!")