import pandas as pd
import os

print("Memulai proses ETL Faktual untuk RB General 2025 (Logika Target)...")
file_path = r'data\raw\Kertas Kerja Evaluasi On Going RB 2025_TW4.xlsx'

df_gen = pd.read_excel(file_path, sheet_name='General', skiprows=2)
sub_headers = df_gen.iloc[0].astype(str).str.lower().str.strip()
df_gen.columns = [f'col_{i}' for i in range(len(df_gen.columns))]

# Auto-Seeker Target & Realisasi
idx_t1 = next((i for i, x in enumerate(sub_headers) if x in ['tw 1', 'tw i']), -1)
idx_t2 = next((i for i, x in enumerate(sub_headers) if x in ['tw 2', 'tw ii']), -1)
idx_t3 = next((i for i, x in enumerate(sub_headers) if x in ['tw 3', 'tw iii']), -1)
idx_t4 = next((i for i, x in enumerate(sub_headers) if x in ['tw 4', 'tw iv']), -1)
idx_target = [idx_t1, idx_t2, idx_t3, idx_t4]

idx_capaian = [i for i, x in enumerate(sub_headers) if x.startswith('capaian')]
idx_kendala = [i for i, x in enumerate(sub_headers) if x.startswith('kendala')]
idx_solusi  = [i for i, x in enumerate(sub_headers) if x.startswith('solusi')]

df_bersih = pd.DataFrame({
    'indikator_utama': df_gen.get('col_1'),
    'rencana_aksi_desc': df_gen.get('col_5'),
    'pic_pelaksana': df_gen.get('col_14'),
})

for tw in range(4):
    if tw < len(idx_target) and idx_target[tw] != -1: 
        df_bersih[f'tw{tw+1}_target'] = df_gen.get(f'col_{idx_target[tw]}')
    if tw < len(idx_capaian): df_bersih[f'tw{tw+1}_capaian_raw'] = df_gen.get(f'col_{idx_capaian[tw]}')
    if tw < len(idx_kendala): df_bersih[f'tw{tw+1}_kendala'] = df_gen.get(f'col_{idx_kendala[tw]}')
    if tw < len(idx_solusi):  df_bersih[f'tw{tw+1}_solusi']  = df_gen.get(f'col_{idx_solusi[tw]}')

df_bersih = df_bersih.iloc[1:].reset_index(drop=True)
df_bersih['indikator_utama'] = df_bersih['indikator_utama'].ffill()
df_bersih = df_bersih.dropna(subset=['rencana_aksi_desc'])

# Fungsi Logika Bisnis Pencapaian
def hitung_status(target, capaian):
    try: t = float(target)
    except: t = 0.0
    
    try: c = float(str(capaian).replace('%', '').replace(',', '.').strip())
    except: c = 0.0
    
    if t > 0:
        pct = (c / t) * 100
        return min(pct, 100.0), "Normal"
    else:
        if c > 0: return 100.0, "Tercapai Lebih Awal"
        else: return 0.0, "Belum Ada Target"

for tw in range(1, 5):
    if f'tw{tw}_target' in df_bersih.columns and f'tw{tw}_capaian_raw' in df_bersih.columns:
        hasil = df_bersih.apply(lambda row: hitung_status(row[f'tw{tw}_target'], row[f'tw{tw}_capaian_raw']), axis=1)
        df_bersih[f'tw{tw}_capaian'] = [res[0] for res in hasil]
        df_bersih[f'tw{tw}_status'] = [res[1] for res in hasil]

os.makedirs(r'data\processed', exist_ok=True)
df_bersih.to_csv(r'data\processed\master_general_2025.csv', index=False)
print("✅ ETL General 2025 Sukses (Dengan Logika Target)!")