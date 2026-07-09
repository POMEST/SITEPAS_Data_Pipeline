import pandas as pd
import os

print("Memulai proses ETL Faktual untuk RB Tematik 2025 (Strict Numeric & Custom Status)...")
file_path = r'data\raw\Kertas Kerja Evaluasi On Going RB 2025_TW4.xlsx'

df_raw = pd.read_excel(file_path, sheet_name='Tematik', header=None)
df_data = df_raw.iloc[5:].reset_index(drop=True)

# INDEX MAPPING KHUSUS SHEET TEMATIK
df_bersih = pd.DataFrame({
    'indikator_utama': df_data[1].ffill(),    # Tema
    'rencana_aksi_desc': df_data[7],          # Rencana Aksi
    'satuan': df_data[9],                     # Satuan Output
    'pic_pelaksana': df_data[17],             # Koordinator/PJK
    
    'tw1_target_raw': df_data[10],
    'tw2_target_raw': df_data[11],
    'tw3_target_raw': df_data[12],
    'tw4_target_raw': df_data[13],
    
    'tw1_capaian_raw': df_data[20],
    'tw2_capaian_raw': df_data[25],
    'tw3_capaian_raw': df_data[30],
    'tw4_capaian_raw': df_data[35],
    
    'tw4_kendala': df_data[37],
    'tw4_solusi': df_data[38],
})

df_bersih = df_bersih.dropna(subset=['rencana_aksi_desc'])
df_bersih = df_bersih[~df_bersih['rencana_aksi_desc'].astype(str).str.contains('Rencana Aksi', case=False)]

def get_number(val, fallback=0.0):
    if pd.isna(val): return 0.0
    s = str(val).strip().lower()
    if s in ['-', '', 'nan', 'none']: return 0.0
    s = s.replace('%', '').replace(',', '.')
    try:
        return float(s)
    except ValueError:
        return float(fallback)

for tw in range(1, 5):
    target_clean, capaian_persen, status_list = [], [], []
    
    for i in range(len(df_bersih)):
        t_raw = df_bersih.iloc[i][f'tw{tw}_target_raw']
        c_raw = df_bersih.iloc[i][f'tw{tw}_capaian_raw']
        tw4_t_raw = df_bersih.iloc[i]['tw4_target_raw']
        
        t = get_number(t_raw, 0.0)
        c = get_number(c_raw, fallback=t)
        tw4_t = get_number(tw4_t_raw, 0.0)
        
        is_percent = (tw4_t == 100.0 or tw4_t == 1.0)
        if is_percent:
            if t > 1.0 and (0.0 < c <= 1.0): c = c * 100.0
            elif c > 1.0 and (0.0 < t <= 1.0): t = t * 100.0
                
        target_clean.append(t)
        
        if t == 0:
            if c > 0:
                capaian_persen.append(100.0)
                status_list.append("Tercapai Lebih Awal")
            else:
                capaian_persen.append(0.0)
                status_list.append("Belum Ada Target Pada TW Ini")
        else:
            pct = (c / t) * 100.0
            capaian_persen.append(min(pct, 100.0))
            if c == t: status_list.append("Tercapai")
            elif c > t: status_list.append("Tercapai Melebihi Target")
            elif c < t: status_list.append("Belum Tercapai Pada TW Ini")
                
    df_bersih[f'tw{tw}_target'] = target_clean
    df_bersih[f'tw{tw}_capaian'] = capaian_persen
    df_bersih[f'tw{tw}_status'] = status_list
    df_bersih = df_bersih.drop(columns=[f'tw{tw}_target_raw', f'tw{tw}_capaian_raw'])

os.makedirs(r'data\processed', exist_ok=True)
df_bersih.to_csv(r'data\processed\master_tematik_2025.csv', index=False)
print("✅ ETL Tematik 2025 Sukses!")