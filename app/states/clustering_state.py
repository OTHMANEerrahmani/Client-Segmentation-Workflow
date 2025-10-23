import reflex as rx
import pandas as pd
import numpy as np
from typing import Literal, Optional
import io
import logging
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score
from app.states.pca_state import PCAState

CLUSTER_COLORS = ["#3b82f6", "#10b981", "#f97316", "#8b5cf6", "#ec4899", "#ef4444"]


class ClusteringState(rx.State):
    selected_algorithm: Literal["KMeans", "Hierarchical"] = "KMeans"
    n_clusters: int = 4
    is_running_clustering: bool = False
    clustering_done: bool = False
    kmeans_silhouette: Optional[float] = None
    hierarchical_silhouette: Optional[float] = None
    kmeans_clusters: int = 0
    hierarchical_clusters: int = 0
    scatter_plot_data: list[dict] = []
    dendrogram_image: Optional[str] = None

    @rx.var
    def get_scatter_data_for_cluster(self) -> list[list[dict]]:
        if not self.scatter_plot_data:
            return []
        num_clusters = max([d.get("cluster", -1) for d in self.scatter_plot_data]) + 1
        return [
            [d for d in self.scatter_plot_data if d.get("cluster") == i]
            for i in range(num_clusters)
        ]

    @rx.event(background=True)
    async def run_clustering(self):
        async with self:
            self.is_running_clustering = True
            yield
        try:
            async with self:
                pca_state = await self.get_state(PCAState)
            if not pca_state.pca_transformed_data_json:
                yield rx.toast.error("PCA data not available. Please run PCA first.")
                async with self:
                    self.is_running_clustering = False
                return
            pca_df = pd.read_json(
                io.StringIO(pca_state.pca_transformed_data_json), orient="split"
            )
            kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
            kmeans_labels = kmeans.fit_predict(pca_df)
            kmeans_silhouette = silhouette_score(pca_df, kmeans_labels)
            hierarchical = AgglomerativeClustering(n_clusters=self.n_clusters)
            hierarchical_labels = hierarchical.fit_predict(pca_df)
            hierarchical_silhouette = silhouette_score(pca_df, hierarchical_labels)
            labels = (
                kmeans_labels
                if self.selected_algorithm == "KMeans"
                else hierarchical_labels
            )
            scatter_data = []
            for i in range(len(pca_df)):
                scatter_data.append(
                    {
                        "x": pca_df.iloc[i, 0],
                        "y": pca_df.iloc[i, 1],
                        "cluster": int(labels[i]),
                    }
                )
            linked = linkage(pca_df, method="ward")
            plt.figure(figsize=(12, 6))
            dendrogram(
                linked,
                orientation="top",
                distance_sort="descending",
                show_leaf_counts=True,
            )
            plt.title("Hierarchical Clustering Dendrogram")
            plt.xlabel("Sample Index")
            plt.ylabel("Distance")
            img_bytes = io.BytesIO()
            plt.savefig(img_bytes, format="png", bbox_inches="tight")
            img_bytes.seek(0)
            dendrogram_filename = f"dendrogram_{pca_state.n_components}.png"
            dendrogram_path = rx.get_upload_dir() / dendrogram_filename
            with dendrogram_path.open("wb") as f:
                f.write(img_bytes.read())
            async with self:
                self.kmeans_silhouette = round(kmeans_silhouette, 4)
                self.hierarchical_silhouette = round(hierarchical_silhouette, 4)
                self.kmeans_clusters = self.n_clusters
                self.hierarchical_clusters = self.n_clusters
                self.scatter_plot_data = scatter_data
                self.dendrogram_image = dendrogram_filename
                self.clustering_done = True
                self.is_running_clustering = False
        except Exception as e:
            logging.exception(f"Clustering failed: {e}")
            async with self:
                self.is_running_clustering = False
            yield rx.toast.error(f"Clustering failed: {e}")