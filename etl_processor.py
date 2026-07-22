import pandas as pd
import os

def etl_rencana_aksi_lengkap(file_path, sheet_name):
    print(f"Memproses sheet: {sheet_name}...")
    
    # 1. Ekstraksi Data
    df_raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    df_data = df_raw.iloc[5:].reset_index(drop=True)
    
    # 2. Pemetaan Kolom (Mencakup data Kualitatif)
    # Catatan: Indeks ini berdasarkan standar file General BPS yang Anda miliki. 
    # Jika di sheet Tematik bergeser 1-2 kolom, Anda bisa menyesuaikan angkanya.
    df_bersih = pd.DataFrame({
        'Kategori': sheet_name, # Menandai dari sheet mana data ini berasal
        'Kegiatan Utama': df_data[1].ffill(),
        'Indikator Kegiatan Utama': df_data[2].ffill(),
        'Rencana Aksi': df_data[5],
        'Output Satuan': df_data[6],
        'PIC Pelaksana': df_data[14],
        
        # Target Angka
        'Target TW 1': df_data[8],
        'Target TW 2': df_data[9],
        'Target TW 3': df_data[10],
        'Target TW 4': df_data[11],
        
        # Capaian Angka
        'Capaian TW 1': df_data[17],
        'Capaian TW 2': df_data[23],
        'Capaian TW 3': df_data[29],
        'Capaian TW 4': df_data[35],
        
        # Narasi Kualitatif (Kendala & Solusi di TW 4 - indeks 37 & 38)
        'Kendala TW 4': df_data[37],
        'Solusi TW 4': df_data[38],
        
        # Catatan Evaluator (Biasanya ada di kolom ujung kanan Excel, misal 40 atau 41)
        # (Silakan sesuaikan indeks di bawah dengan letak kolom di Excel Anda)
        'Catatan Evaluator TW4': df_data.iloc[:, -1] # Mengambil kolom paling terakhir
    })

    # Bersihkan baris kosong atau header berulang
    df_bersih = df_bersih.dropna(subset=['Rencana Aksi'])
    df_bersih = df_bersih[~df_bersih['Rencana Aksi'].astype(str).str.contains('Rencana Aksi', case=False)]
    
    # Isi data kualitatif yang kosong dengan "Tidak ada" agar AI mudah membaca
    kolom_teks = ['Kendala TW 4', 'Solusi TW 4', 'Catatan Evaluator TW4']
    df_bersih[kolom_teks] = df_bersih[kolom_teks].fillna('Tidak ada keterangan')
    
    return df_bersih


# ================= PROSES UTAMA =================
file_path_raw = r'data\raw\Kertas Kerja Evaluasi On Going RB 2025_TW4.xlsx'

# Menggabungkan ketiga sheet menjadi satu Super-Tabel
daftar_sheet = ['General', 'Tematik', 'Tematik Baru']
df_gabungan = pd.DataFrame()

for sheet in daftar_sheet:
    try:
        df_sheet = etl_rencana_aksi_lengkap(file_path_raw, sheet)
        df_gabungan = pd.concat([df_gabungan, df_sheet], ignore_index=True)
    except Exception as e:
        print(f"Gagal memproses sheet {sheet}: {e}")

# Menyimpan hasil ke satu master CSV lengkap
os.makedirs(r'data\processed', exist_ok=True)
path_simpan = r'data\processed\master_seluruh_data_2025_lengkap.csv'
df_gabungan.to_csv(path_simpan, index=False)

print(f"✅ ETL Sukses! Semua data angka dan teks kualitatif telah digabung menjadi satu di: {path_simpan}")