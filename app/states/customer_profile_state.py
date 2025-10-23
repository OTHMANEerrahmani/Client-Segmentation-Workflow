import reflex as rx
import pandas as pd
import numpy as np
from typing import TypedDict, Optional
import io
import logging
from app.states.data_cleaning_state import DataCleaningState
from app.states.clustering_state import ClusteringState


class ProfileFeature(TypedDict):
    feature: str
    value: str
    avg_value: float


class SegmentProfile(TypedDict):
    cluster_id: int
    label: str
    count: int
    percentage: float
    top_features: list[ProfileFeature]


class CustomerProfileState(rx.State):
    profiles_generated: bool = False
    is_generating: bool = False
    segment_profiles: list[SegmentProfile] = []
    cluster_summary_stats: list[dict] = []
    cluster_summary_columns: list[str] = []

    @rx.event(background=True)
    async def generate_profiles(self):
        async with self:
            self.is_generating = True
            yield
        try:
            async with self:
                cleaning_state = await self.get_state(DataCleaningState)
                clustering_state = await self.get_state(ClusteringState)
            if (
                not clustering_state.clustering_done
                or not cleaning_state.cleaned_df_json
            ):
                yield rx.toast.error(
                    "Required data not available. Please complete previous steps."
                )
                async with self:
                    self.is_generating = False
                return
            df = pd.read_json(
                io.StringIO(cleaning_state.cleaned_df_json), orient="split"
            )
            scatter_data = clustering_state.scatter_plot_data
            df["cluster"] = [d["cluster"] for d in scatter_data]
            numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
            if "cluster" in numeric_cols:
                numeric_cols.remove("cluster")
            summary_stats = df.groupby("cluster")[numeric_cols].mean().reset_index()
            total_customers = len(df)
            profiles = []
            for i, row in summary_stats.iterrows():
                cluster_id = int(row["cluster"])
                cluster_data = df[df["cluster"] == cluster_id]
                count = len(cluster_data)
                percentage = count / total_customers * 100
                cluster_means = cluster_data[numeric_cols].mean()
                overall_means = df[numeric_cols].mean()
                ratio = (cluster_means / overall_means.replace(0, 1e-06)).abs()
                top_feature_indices = ratio.nlargest(3).index
                top_features_list = []
                for feature in top_feature_indices:
                    top_features_list.append(
                        {
                            "feature": feature,
                            "value": f"{cluster_means[feature]:.2f}",
                            "avg_value": overall_means[feature],
                        }
                    )
                label = f"Segment {cluster_id + 1}"
                if "Monthly Income (€)" in top_feature_indices:
                    if (
                        cluster_means["Monthly Income (€)"]
                        > overall_means["Monthly Income (€)"] * 1.2
                    ):
                        label = f"High-Income Earners {cluster_id + 1}"
                elif "Savings Amount (€)" in top_feature_indices:
                    if (
                        cluster_means["Savings Amount (€)"]
                        > overall_means["Savings Amount (€)"] * 1.2
                    ):
                        label = f"Premium Savers {cluster_id + 1}"
                profiles.append(
                    {
                        "cluster_id": cluster_id,
                        "label": label,
                        "count": count,
                        "percentage": round(percentage, 2),
                        "top_features": top_features_list,
                    }
                )
            async with self:
                self.segment_profiles = profiles
                self.cluster_summary_columns = ["cluster"] + numeric_cols
                self.cluster_summary_stats = summary_stats.round(2).to_dict(
                    orient="records"
                )
                self.profiles_generated = True
                self.is_generating = False
        except Exception as e:
            logging.exception(f"Profile generation failed: {e}")
            async with self:
                self.is_generating = False
            yield rx.toast.error(f"Profile generation failed: {str(e)}")

    @rx.event
    def download_segmented_data(self) -> rx.event.EventSpec:
        clustering_state = self.get_state_sync(ClusteringState)
        cleaning_state = self.get_state_sync(DataCleaningState)
        df = pd.read_json(io.StringIO(cleaning_state.cleaned_df_json), orient="split")
        df["cluster"] = [d["cluster"] for d in clustering_state.scatter_plot_data]
        csv_string = df.to_csv(index=False)
        return rx.download(data=csv_string.encode(), filename="customer_segments.csv")