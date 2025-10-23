import reflex as rx
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from typing import Union, Any, TypedDict
import plotly.express as px
import plotly.graph_objects as go
import io
import logging
from app.states.data_cleaning_state import DataCleaningState


class FeatureContribution(TypedDict):
    name: str
    value: float


class ComponentContribution(TypedDict):
    component: str
    features: list[FeatureContribution]


class PCAState(rx.State):
    is_running_pca: bool = False
    pca_done: bool = False
    n_components: int = 0
    explained_variance_ratio: list[float] = []
    cumulative_variance: list[float] = []
    component_contributions: list[ComponentContribution] = []
    scree_plot: go.Figure | None = None
    cumulative_variance_plot: go.Figure | None = None
    pca_summary: str = ""
    pca_transformed_data_json: str = ""

    @rx.var
    def scree_plot_data(self) -> list[dict[str, Union[int, float]]]:
        return [
            {"component": i + 1, "variance": v}
            for i, v in enumerate(self.explained_variance_ratio)
        ]

    @rx.var
    def cumulative_variance_data(self) -> list[dict[str, Union[int, float]]]:
        return [
            {"component": i + 1, "cumulative_variance": v}
            for i, v in enumerate(self.cumulative_variance)
        ]

    @rx.event(background=True)
    async def run_pca(self):
        async with self:
            self.is_running_pca = True
            self.pca_done = False
            yield
        try:
            async with self:
                data_cleaning_state = await self.get_state(DataCleaningState)
            if not data_cleaning_state.cleaned_df_json:
                yield rx.toast.error(
                    "No cleaned data available. Please complete data cleaning first."
                )
                async with self:
                    self.is_running_pca = False
                return
            df = pd.read_json(
                io.StringIO(data_cleaning_state.cleaned_df_json), orient="split"
            )
            numeric_cols = df.select_dtypes(include=np.number).columns
            df_numeric = df[numeric_cols]
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(df_numeric)
            pca = PCA()
            pca.fit(scaled_data)
            cumulative_variance = np.cumsum(pca.explained_variance_ratio_)
            n_components = np.where(cumulative_variance >= 0.8)[0][0] + 1
            pca = PCA(n_components=n_components)
            pca_result = pca.fit_transform(scaled_data)
            contributions = []
            for i, component in enumerate(pca.components_):
                abs_loadings = np.abs(component)
                sorted_indices = np.argsort(abs_loadings)[::-1]
                comp_data = {"component": f"PC {i + 1}", "features": []}
                for j in sorted_indices[:5]:
                    comp_data["features"].append(
                        {"name": numeric_cols[j], "value": component[j]}
                    )
                contributions.append(comp_data)
            async with self:
                self.pca_transformed_data_json = pd.DataFrame(pca_result).to_json(
                    orient="split"
                )
                self.n_components = int(n_components)
                self.explained_variance_ratio = [
                    float(v) for v in pca.explained_variance_ratio_
                ]
                self.cumulative_variance = [
                    float(v) for v in np.cumsum(pca.explained_variance_ratio_)
                ]
                self.component_contributions = contributions
                self.pca_summary = f"PCA selected {self.n_components} components, which collectively explain {self.cumulative_variance[-1]:.2%} of the total variance in the dataset. This allows us to reduce dimensionality while retaining the most significant information."
                self.is_running_pca = False
                self.pca_done = True
        except Exception as e:
            logging.exception(f"PCA failed: {e}")
            async with self:
                self.is_running_pca = False
            yield rx.toast.error(f"PCA analysis failed: {e}")