import reflex as rx
import pandas as pd
import numpy as np
from typing import Optional, Union
import io
import logging
import matplotlib.pyplot as plt
import seaborn as sns


class DataCleaningState(rx.State):
    uploaded_file: str = ""
    raw_df_preview: list[dict[str, Union[str, int, float]]] = []
    raw_df_columns: list[str] = []
    cleaned_df_preview: list[dict[str, Union[str, int, float]]] = []
    cleaned_df_json: str = ""
    is_cleaning: bool = False
    cleaning_done: bool = False
    uploading: bool = False
    correlation_heatmap: Optional[str] = None
    initial_rows: int = 0
    missing_values_before: int = 0
    outliers_before: int = 0
    cleaned_rows: int = 0
    missing_values_after: int = 0
    outliers_after: int = 0

    @rx.var
    def raw_data_preview_limited(self) -> list[dict[str, Union[str, int, float]]]:
        return self.raw_df_preview[:10]

    @rx.var
    def missing_value_percentage(self) -> float:
        if self.initial_rows == 0:
            return 0.0
        return (
            round(
                self.missing_values_before
                / (self.initial_rows * len(self.raw_df_columns))
                * 100,
                2,
            )
            if self.raw_df_columns
            else 0
        )

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        if not files:
            yield rx.toast.error("No file selected.")
            return
        self.uploading = True
        yield
        try:
            file = files[0]
            upload_data = await file.read()
            df = pd.read_csv(io.BytesIO(upload_data))
            self.raw_df_columns = df.columns.tolist()
            self.raw_df_preview = df.to_dict(orient="records")
            self.uploaded_file = file.name
            self.initial_rows = len(df)
            self.missing_values_before = int(df.isnull().sum().sum())
            numeric_cols = df.select_dtypes(include=np.number).columns
            q1 = df[numeric_cols].quantile(0.25)
            q3 = df[numeric_cols].quantile(0.75)
            iqr = q3 - q1
            outliers = (df[numeric_cols] < q1 - 1.5 * iqr) | (
                df[numeric_cols] > q3 + 1.5 * iqr
            )
            self.outliers_before = int(outliers.sum().sum())
            self.cleaning_done = False
            self.correlation_heatmap = None
            self.cleaned_df_preview = []
        except Exception as e:
            logging.exception(f"Error processing file: {e}")
            yield rx.toast.error(f"Error processing file: {e}")
        finally:
            self.uploading = False
            yield

    @rx.event
    def load_new_file(self):
        self.uploaded_file = ""
        self.raw_df_preview = []
        self.raw_df_columns = []
        self.cleaned_df_preview = []
        self.cleaned_df_json = ""
        self.cleaning_done = False
        self.correlation_heatmap = None
        self.initial_rows = 0
        self.missing_values_before = 0
        self.outliers_before = 0
        self.cleaned_rows = 0
        self.missing_values_after = 0
        self.outliers_after = 0
        return rx.clear_selected_files("upload_data_cleaning")

    @rx.event(background=True)
    async def start_cleaning(self):
        async with self:
            if not self.raw_df_preview:
                yield rx.toast.error("No data to clean.")
                return
            self.is_cleaning = True
            yield
        try:
            df = pd.DataFrame(self.raw_df_preview)
            cleaned_df = df.copy()
            for col in cleaned_df.columns:
                if cleaned_df[col].dtype == "object":
                    mode = cleaned_df[col].mode()[0]
                    cleaned_df[col] = cleaned_df[col].fillna(mode)
                else:
                    median = cleaned_df[col].median()
                    cleaned_df[col] = cleaned_df[col].fillna(median)
            numeric_cols = cleaned_df.select_dtypes(include=np.number).columns
            for col in numeric_cols:
                q1 = cleaned_df[col].quantile(0.25)
                q3 = cleaned_df[col].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                cleaned_df[col] = np.clip(cleaned_df[col], lower_bound, upper_bound)
            plt.figure(figsize=(10, 8))
            sns.heatmap(
                cleaned_df.corr(numeric_only=True), annot=True, cmap="vlag", fmt=".2f"
            )
            plt.title("Feature Correlation Heatmap")
            plt.xticks(rotation=45, ha="right")
            plt.yticks(rotation=0)
            plt.tight_layout()
            img_bytes = io.BytesIO()
            plt.savefig(img_bytes, format="png")
            img_bytes.seek(0)
            heatmap_filename = (
                f"correlation_heatmap_{self.uploaded_file.split('.')[0]}.png"
            )
            heatmap_path = rx.get_upload_dir() / heatmap_filename
            with heatmap_path.open("wb") as f:
                f.write(img_bytes.read())
            async with self:
                self.cleaned_df_preview = cleaned_df.to_dict(orient="records")
                self.cleaned_df_json = cleaned_df.to_json(orient="split")
                self.cleaned_rows = len(cleaned_df)
                self.missing_values_after = int(cleaned_df.isnull().sum().sum())
                outliers_after_df = (
                    cleaned_df[numeric_cols]
                    < cleaned_df[numeric_cols].quantile(0.25)
                    - 1.5
                    * (
                        cleaned_df[numeric_cols].quantile(0.75)
                        - cleaned_df[numeric_cols].quantile(0.25)
                    )
                ) | (
                    cleaned_df[numeric_cols]
                    > cleaned_df[numeric_cols].quantile(0.75)
                    + 1.5
                    * (
                        cleaned_df[numeric_cols].quantile(0.75)
                        - cleaned_df[numeric_cols].quantile(0.25)
                    )
                )
                self.outliers_after = int(outliers_after_df.sum().sum())
                self.correlation_heatmap = heatmap_filename
                self.is_cleaning = False
                self.cleaning_done = True
        except Exception as e:
            logging.exception(f"Cleaning failed: {e}")
            async with self:
                self.is_cleaning = False
            yield rx.toast.error(f"Cleaning failed: {e}")