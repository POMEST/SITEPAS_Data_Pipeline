import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def jalankan_kmeans(df, n_clusters=4):
    """
    Fungsi untuk melakukan K-Means Clustering pada data Rencana Aksi BPS.
    Diperbarui: Menggunakan rasio pencapaian target dan labeling klaster dinamis.
    """
    if df.empty:
        return df

    df_proses = df.copy()

    # Pastikan data yang diperlukan ada
    kolom_wajib = [
        'target tw 1', 'target tw 2', 'target tw 3', 'target tw 4',
        'capaian output tw 1', 'capaian output tw 2', 'capaian output tw 3', 'capaian output tw 4'
    ]
    
    # Jika tidak lengkap, kembalikan data apa adanya
    for col in kolom_wajib:
        if col not in df_proses.columns:
            return df_proses
            
    # Konversi ke numerik
    for col in kolom_wajib:
        df_proses[col] = pd.to_numeric(df_proses[col], errors='coerce').fillna(0)

    # 1. Feature Engineering: Hitung rasio capaian per target
    df_fitur = pd.DataFrame()
    for i in range(1, 5):
        target_col = f'target tw {i}'
        capaian_col = f'capaian output tw {i}'
        
        rasio = np.where(
            df_proses[target_col] > 0,
            df_proses[capaian_col] / df_proses[target_col],
            np.where(df_proses[capaian_col] > 0, 1.0, 0.0) 
        )
        # Clip max 1.5 agar overachiever tidak mendominasi model K-Means (outlier limit)
        df_fitur[f'rasio_tw_{i}'] = np.clip(rasio, 0.0, 1.5)

    # 2. Standarisasi Data
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(df_fitur)

    # 3. Eksekusi K-Means
    n_clusters_actual = min(n_clusters, len(df_fitur))
    
    if n_clusters_actual < 2:
        df_proses['Label_Klaster'] = "Klaster Tunggal (Data Sedikit)"
        return df_proses

    kmeans = KMeans(n_clusters=n_clusters_actual, random_state=42, n_init=10)
    df_proses['Cluster_ID'] = kmeans.fit_predict(data_scaled)

    # 4. Pelabelan Dinamis Berdasarkan Centroid
    centroids = scaler.inverse_transform(kmeans.cluster_centers_)
    cluster_scores = centroids.sum(axis=1)
    sorted_cluster_indices = np.argsort(cluster_scores)
    
    cluster_labels = {}
    for i, cluster_idx in enumerate(sorted_cluster_indices):
        centroid = centroids[cluster_idx]
        total_score = cluster_scores[cluster_idx]
        proporsi_tw4 = centroid[3] / (total_score + 1e-9)
        
        if i == 0:
            cluster_labels[cluster_idx] = "Klaster Kritis / Tertinggal"
        elif i == len(sorted_cluster_indices) - 1:
            cluster_labels[cluster_idx] = "Klaster Tuntas & Progresif"
        else:
            if proporsi_tw4 > 0.6:
                cluster_labels[cluster_idx] = "Klaster Lonjakan Akhir (SKS)"
            else:
                cluster_labels[cluster_idx] = "Klaster Performa Moderat"
                
    # Menghindari duplikasi nama
    from collections import Counter
    label_counts = Counter(cluster_labels.values())
    seen = {}
    for k, v in cluster_labels.items():
        if label_counts[v] > 1:
            seen[v] = seen.get(v, 0) + 1
            cluster_labels[k] = f"{v} (Tipe {seen[v]})"

    df_proses['Label_Klaster'] = df_proses['Cluster_ID'].map(cluster_labels)

    return df_proses