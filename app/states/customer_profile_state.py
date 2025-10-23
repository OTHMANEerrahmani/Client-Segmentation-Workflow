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
    async def download_segmented_data(self):
        async with self:
            cleaning_state = await self.get_state(DataCleaningState)
            clustering_state = await self.get_state(ClusteringState)
        if not clustering_state.clustering_done or not cleaning_state.cleaned_df_json:
            return rx.toast.error("No segmented data to download.")
        try:
            df = pd.read_json(
                io.StringIO(cleaning_state.cleaned_df_json), orient="split"
            )
            scatter_data = clustering_state.scatter_plot_data
            df["cluster"] = [d["cluster"] for d in scatter_data]
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            return rx.download(
                data=csv_buffer.getvalue(), filename="segmented_customer_data.csv"
            )
        except Exception as e:
            logging.exception(f"Failed to download segmented data: {e}")
            return rx.toast.error("Failed to generate download file.")

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
            summary_stats_df = df.groupby("cluster")[numeric_cols].mean().reset_index()
            total_customers = len(df)
            profiles = []
            for i, row in summary_stats_df.iterrows():
                cluster_id = int(row["cluster"])
                cluster_data = df[df["cluster"] == cluster_id]
                count = len(cluster_data)
                percentage = count / total_customers * 100
                segment_means = row.drop("cluster")
                overall_means = df[numeric_cols].mean()
                deviations = (segment_means - overall_means) / overall_means
                top_features_indices = deviations.abs().nlargest(3).index
                top_features = []
                for feature in top_features_indices:
                    top_features.append(
                        {
                            "feature": feature,
                            "value": f"{segment_means[feature]:.2f}",
                            "avg_value": segment_means[feature],
                        }
                    )
                profiles.append(
                    {
                        "cluster_id": cluster_id,
                        "label": f"Segment {cluster_id + 1}",
                        "count": count,
                        "percentage": percentage,
                        "top_features": top_features,
                    }
                )
            async with self:
                self.segment_profiles = profiles
                summary_stats_df["cluster"] = summary_stats_df["cluster"].apply(
                    lambda x: f"Segment {x + 1}"
                )
                self.cluster_summary_columns = summary_stats_df.columns.tolist()
                self.cluster_summary_stats = summary_stats_df.round(2).to_dict(
                    orient="records"
                )
                self.profiles_generated = True
        except Exception as e:
            logging.exception(f"Profile generation failed: {e}")
            yield rx.toast.error(f"Profile generation failed: {str(e)}")
        finally:
            async with self:
                self.is_generating = False