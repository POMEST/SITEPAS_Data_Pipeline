import pandas as pd
import os
import re

print("Memulai Deep-Scan ETL untuk Data 2025 (General, Tematik, Tematik Baru)...")
file_path = r'data\raw\Kertas Kerja Evaluasi On Going RB 2025_TW4.xlsx'

sheets = [
    ('General', 1, 5, 14),       # (Sheet, Index Tema, Index Aksi, Index PIC)
    ('Tematik', 1, 7, 16),
    ('Tematik Baru', 1, 9, 18)
]

for sheet_name, idx_tema, idx_aksi, idx_pic in sheets:
    print(f"Mengekstrak sheet: {sheet_name}...")
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=2)
    except Exception as e:
        continue

    # Menggunakan Baris ke-4 Excel sebagai kunci mutlak!
    row4 = df.iloc[0].astype(str).str.lower().str.strip()

    idx_t1 = next((i for i, x in enumerate(row4) if x in ['tw 1', 'tw i']), -1)
    idx_t2 = next((i for i, x in enumerate(row4) if x in ['tw 2', 'tw ii']), -1)
    idx_t3 = next((i for i, x in enumerate(row4) if x in ['tw 3', 'tw iii']), -1)
    idx_t4 = next((i for i, x in enumerate(row4) if x in ['tw 4', 'tw iv']), -1)
    idx_target = [idx_t1, idx_t2, idx_t3, idx_t4]

    idx_capaian = [i for i, x in enumerate(row4) if 'capaian' in x and 'realisasi' not in x]
    idx_kendala = [i for i, x in enumerate(row4) if 'kendala' in x]
    idx_solusi  = [i for i, x in enumerate(row4) if 'solusi' in x]

    df_bersih = pd.DataFrame()
    df_bersih['indikator_utama'] = df.iloc[:, idx_tema]
    if sheet_name == 'Tematik Baru': df_bersih['penyesuaian_tema'] = df.iloc[:, 2]
    df_bersih['rencana_aksi_desc'] = df.iloc[:, idx_aksi]
    df_bersih['pic_pelaksana'] = df.iloc[:, idx_pic]

    for tw in range(4):
        df_bersih[f'tw{tw+1}_target'] = df.iloc[:, idx_target[tw]] if tw < len(idx_target) and idx_target[tw] != -1 else 0
        df_bersih[f'tw{tw+1}_capaian_raw'] = df.iloc[:, idx_capaian[tw]] if tw < len(idx_capaian) else 0
        df_bersih[f'tw{tw+1}_kendala'] = df.iloc[:, idx_kendala[tw]] if tw < len(idx_kendala) else ""
        df_bersih[f'tw{tw+1}_solusi'] = df.iloc[:, idx_solusi[tw]] if tw < len(idx_solusi) else ""

    df_bersih = df_bersih.iloc[2:].reset_index(drop=True)
    df_bersih['indikator_utama'] = df_bersih['indikator_utama'].ffill()
    df_bersih = df_bersih.dropna(subset=['rencana_aksi_desc'])

    def hitung_status(target, capaian):
        try: t = float(target)
        except: t = 0.0
        try: c = float(str(capaian).replace('%', '').replace(',', '.').strip())
        except: c = 0.0
        
        if t > 0: return min((c / t) * 100, 100.0), "Normal"
        else: return (100.0, "Tercapai Lebih Awal") if c > 0 else (0.0, "Belum Ada Target")

    for tw in range(1, 5):
        hasil = df_bersih.apply(lambda row: hitung_status(row[f'tw{tw}_target'], row[f'tw{tw}_capaian_raw']), axis=1)
        df_bersih[f'tw{tw}_capaian'] = [res[0] for res in hasil]
        df_bersih[f'tw{tw}_status'] = [res[1] for res in hasil]

    os.makedirs(r'data\processed', exist_ok=True)
    nama_file = 'master_general_2025.csv' if sheet_name == 'General' else 'master_tematik_2025.csv' if sheet_name == 'Tematik' else 'master_tematik_baru_2025.csv'
    df_bersih.to_csv(os.path.join('data', 'processed', nama_file), index=False)
    print(f"✅ Selesai memproses {sheet_name}!")