import pandas as pd
import os

print("Memulai proses ETL Faktual untuk RB General 2025 (Kustomisasi Penuh)...")
file_path = r'data\raw\Kertas Kerja Evaluasi On Going RB 2025_TW4.xlsx'

# 1. Ekstraksi Data (Mencari letak kolom spesifik dari format excel mentah)
df_raw = pd.read_excel(file_path, sheet_name='General', header=None)
df_data = df_raw.iloc[5:].reset_index(drop=True)

df_bersih = pd.DataFrame({
    'kegiatan utama': df_data[1].ffill(),
    'indikator kegiatan utama': df_data[2].ffill(),
    'Rencana Aksi': df_data[5],
    'output(Satuan)': df_data[6],
    'pic_pelaksana': df_data[14],
    'target tw 1': df_data[8],
    'target tw 2': df_data[9],
    'target tw 3': df_data[10],
    'target tw 4': df_data[11],
    'capaian output tw 1': df_data[17],
    'capaian output tw 2': df_data[23],
    'capaian output tw 3': df_data[29],
    'capaian output tw 4': df_data[35],
})

# Menghapus baris kosong dan baris header berulang
df_bersih = df_bersih.dropna(subset=['Rencana Aksi'])
df_bersih = df_bersih[~df_bersih['Rencana Aksi'].astype(str).str.contains('Rencana Aksi', case=False)]

# 2. Fungsi Pengubah Nilai Angka
def parse_val(val, fallback_val):
    if pd.isna(val): return 0.0
    val_str = str(val).strip().lower()
    if val_str in ['-', '', 'nan', 'none']: return 0.0
    
    # Hapus simbol persentase dan ganti koma jadi titik
    val_str = val_str.replace('%', '').replace(',', '.')
    
    try:
        return float(val_str)
    except ValueError:
        # Jika error (karena ada teks/huruf), kembalikan ke nilai target (fallback_val)
        return float(fallback_val)

def get_status(t, c):
    if t == 0 and c == 0:
        return "Tidak Ada Target"
    elif c >= t:
        return "Target Tercapai"
    else:
        return "Tidak Tercapai"

# 3. Proses Transformasi, Normalisasi & Penentuan Status
new_rows = []
for idx, row in df_bersih.iterrows():
    # Ambil target numerik awal
    t1 = parse_val(row['target tw 1'], 0.0)
    t2 = parse_val(row['target tw 2'], 0.0)
    t3 = parse_val(row['target tw 3'], 0.0)
    t4 = parse_val(row['target tw 4'], 0.0)
    
    # Ambil capaian (fallback otomatis kembali ke target TW tsb jika berupa teks)
    c1 = parse_val(row['capaian output tw 1'], fallback_val=t1)
    c2 = parse_val(row['capaian output tw 2'], fallback_val=t2)
    c3 = parse_val(row['capaian output tw 3'], fallback_val=t3)
    c4 = parse_val(row['capaian output tw 4'], fallback_val=t4)
    
    # Aturan Desimal: jika target tw 4 = 100, ubah angka 1-100 menjadi 0.0-1.0
    if t4 == 100.0:
        t1, t2, t3, t4 = t1/100, t2/100, t3/100, t4/100
        c1, c2, c3, c4 = c1/100, c2/100, c3/100, c4/100
        
    # Penentuan Status per Kuartal
    s1 = get_status(t1, c1)
    s2 = get_status(t2, c2)
    s3 = get_status(t3, c3)
    s4 = get_status(t4, c4)
    
    # Perhitungan Persentase Keseluruhan (Tidak Ada Target dinilai Tercapai/Aman)
    statuses = [s1, s2, s3, s4]
    score = sum(1 for s in statuses if s in ["Target Tercapai", "Tidak Ada Target"])
    pct = f"{int((score / 4) * 100)}%"
    
    new_rows.append({
        'kegiatan utama': row['kegiatan utama'],
        'indikator kegiatan utama': row['indikator kegiatan utama'],
        'Rencana Aksi': row['Rencana Aksi'],
        'output(Satuan)': row['output(Satuan)'],
        'pic_pelaksana': row['pic_pelaksana'],
        'target tw 1': t1,
        'target tw 2': t2,
        'target tw 3': t3,
        'target tw 4': t4,
        'capaian output tw 1': c1,
        'capaian output tw 2': c2,
        'capaian output tw 3': c3,
        'capaian output tw 4': c4,
        'status tw 1': s1,
        'status tw 2': s2,
        'status tw 3': s3,
        'status tw 4': s4,
        'Persentase Pencapaian Target': pct
    })

# 4. Simpan ke CSV Baru
df_final = pd.DataFrame(new_rows)
os.makedirs(r'data\processed', exist_ok=True)
df_final.to_csv(r'data\processed\master_general_2025_cleaned.xlsx', index=False)

print("✅ ETL General 2025 Sukses! Format data sudah dinormalisasi dan kolom status siap divisualisasikan.")