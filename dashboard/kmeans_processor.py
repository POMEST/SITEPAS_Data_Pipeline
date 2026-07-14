import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def jalankan_kmeans(df, n_clusters=4):
    """
    Fungsi untuk melakukan K-Means Clustering pada data Rencana Aksi BPS.
    Dilengkapi penanganan error untuk data sedikit dan data non-numerik.
    """
    # 1. Pastikan dataframe tidak kosong
    if df.empty:
        return df

    df_proses = df.copy()

    # 2. Ambil kolom-kolom numerik yang relevan untuk klastering
    kolom_fitur = [
        'target tw 1', 'target tw 2', 'target tw 3', 'target tw 4',
        'capaian output tw 1', 'capaian output tw 2', 'capaian output tw 3', 'capaian output tw 4'
    ]

    # Pastikan kolom ada di dataframe
    fitur_tersedia = [col for col in kolom_fitur if col in df_proses.columns]
    
    # Ekstraksi angka dari kolom persentase jika ada
    if 'Persentase Pencapaian Target' in df_proses.columns:
        # Bersihkan simbol % dan paksa ubah ke angka (numeric)
        df_proses['pct_num'] = df_proses['Persentase Pencapaian Target'].astype(str).str.replace('%', '', regex=False)
        fitur_tersedia.append('pct_num')

    # 3. Filter data dan PAKSA ubah ke numerik (menghindari error string ke float)
    df_fitur = df_proses[fitur_tersedia].copy()
    for col in df_fitur.columns:
        # errors='coerce' akan mengubah teks aneh menjadi NaN, lalu fillna(0) mengubahnya jadi 0
        df_fitur[col] = pd.to_numeric(df_fitur[col], errors='coerce').fillna(0)

    # 4. Standarisasi Data (Z-Score Normalization)
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(df_fitur)

    # 5. Menjalankan Algoritma K-Means (Cerdas membaca jumlah baris)
    # Jika baris data kurang dari 4, maka sesuaikan jumlah klasternya
    n_clusters_actual = min(n_clusters, len(df_fitur))
    
    # Jika baris data kurang dari 2, klastering tidak relevan
    if n_clusters_actual < 2:
        df_proses['Label_Klaster'] = "Klaster Tunggal (Data Sedikit)"
        return df_proses

    # Eksekusi K-Means
    kmeans = KMeans(n_clusters=n_clusters_actual, random_state=42, n_init=10)
    df_proses['Cluster_ID'] = kmeans.fit_predict(data_scaled)

    # 6. Pemetaan Label Klaster
    def get_cluster_label(cluster_id):
        labels = {
            0: "Klaster 0: Performa Moderat",
            1: "Klaster 1: Tuntas & Konsisten",
            2: "Klaster 2: Tertinggal / Kritis",
            3: "Klaster 3: Lonjakan Akhir Tahun (SKS)"
        }
        return labels.get(cluster_id, f"Klaster {cluster_id}")
        
    df_proses['Label_Klaster'] = df_proses['Cluster_ID'].apply(get_cluster_label)

    # Bersihkan kolom sementara
    if 'pct_num' in df_proses.columns:
        df_proses = df_proses.drop(columns=['pct_num'])

    return df_proses