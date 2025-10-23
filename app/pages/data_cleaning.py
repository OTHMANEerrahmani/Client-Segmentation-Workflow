import reflex as rx
from app.states.data_cleaning_state import DataCleaningState


def upload_component() -> rx.Component:
    return rx.el.div(
        rx.upload.root(
            rx.el.div(
                rx.icon("cloud-upload", class_name="h-12 w-12 text-gray-400"),
                rx.el.h3(
                    "Click or drag a file to upload",
                    class_name="mt-4 text-sm font-medium text-gray-700",
                ),
                rx.el.p("CSV up to 10MB", class_name="mt-1 text-xs text-gray-500"),
                class_name="flex flex-col items-center justify-center p-8 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors",
            ),
            id="upload_data_cleaning",
            accept={"text/csv": [".csv"]},
            max_files=1,
            max_size=10000000,
            on_drop=DataCleaningState.handle_upload(
                rx.upload_files(upload_id="upload_data_cleaning")
            ),
            class_name="w-full cursor-pointer",
        ),
        rx.el.div(
            rx.foreach(
                rx.selected_files("upload_data_cleaning"),
                lambda file: rx.el.div(file, class_name="text-sm text-gray-600"),
            )
        ),
        rx.el.button(
            "Upload",
            on_click=DataCleaningState.handle_upload(
                rx.upload_files(upload_id="upload_data_cleaning")
            ),
            is_loading=DataCleaningState.uploading,
            class_name="mt-4 w-full inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 disabled:opacity-50",
        ),
        class_name="w-full max-w-lg mx-auto",
    )


def data_table(columns: rx.Var[list[str]], data: rx.Var[list[dict]]) -> rx.Component:
    return rx.el.div(
        rx.el.table(
            rx.el.thead(
                rx.el.tr(
                    rx.foreach(
                        columns,
                        lambda col: rx.el.th(
                            col,
                            class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                    )
                )
            ),
            rx.el.tbody(
                rx.foreach(
                    data,
                    lambda row: rx.el.tr(
                        rx.foreach(
                            columns,
                            lambda col: rx.el.td(
                                row[col],
                                class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-700",
                            ),
                        ),
                        class_name="odd:bg-white even:bg-gray-50",
                    ),
                ),
                class_name="bg-white divide-y divide-gray-200",
            ),
            class_name="min-w-full divide-y divide-gray-200",
        ),
        class_name="overflow-x-auto rounded-lg border border-gray-200 shadow-sm",
    )


def uploaded_data_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("square-check", class_name="h-6 w-6 text-green-500"),
                rx.el.h3(
                    f"File Uploaded: {DataCleaningState.uploaded_file}",
                    class_name="ml-2 text-lg font-semibold text-gray-800",
                ),
                class_name="flex items-center p-4 bg-green-50 rounded-lg border border-green-200",
            ),
            rx.el.div(
                rx.el.button(
                    "Load New File",
                    on_click=DataCleaningState.load_new_file,
                    class_name="rounded-lg bg-gray-200 px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-300",
                ),
                rx.el.button(
                    "Start Cleaning",
                    on_click=DataCleaningState.start_cleaning,
                    is_loading=DataCleaningState.is_cleaning,
                    class_name="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700 disabled:opacity-50",
                ),
                class_name="flex items-center gap-4 mt-4",
            ),
            class_name="flex justify-between items-center w-full mb-6",
        ),
        data_table(
            columns=DataCleaningState.raw_df_columns,
            data=DataCleaningState.raw_data_preview_limited,
        ),
        class_name="w-full",
    )


def data_quality_card(title: str, value: rx.Var, unit: str, icon: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-6 w-6 text-gray-500"),
            class_name="p-3 bg-gray-100 rounded-full",
        ),
        rx.el.div(
            rx.el.p(title, class_name="text-sm font-medium text-gray-500"),
            rx.el.p(
                value, " ", unit, class_name="text-2xl font-semibold text-gray-900"
            ),
            class_name="ml-4",
        ),
        class_name="flex items-center p-4 bg-white rounded-xl border border-gray-100 shadow-sm",
    )


def cleaning_results_view() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Data Cleaning Results", class_name="text-2xl font-bold text-gray-900 mb-6"
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Data Quality Before Cleaning",
                    class_name="text-lg font-semibold text-gray-800 mb-4",
                ),
                rx.el.div(
                    data_quality_card(
                        title="Total Rows",
                        value=DataCleaningState.initial_rows,
                        unit="",
                        icon="rows",
                    ),
                    data_quality_card(
                        title="Missing Values",
                        value=DataCleaningState.missing_value_percentage,
                        unit="%",
                        icon="circle-help",
                    ),
                    data_quality_card(
                        title="Outliers Detected",
                        value=DataCleaningState.outliers_before,
                        unit="",
                        icon="triangle-alert",
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-3 gap-4",
                ),
                class_name="p-6 bg-gray-50 rounded-2xl border border-gray-200",
            ),
            rx.el.div(
                rx.el.h3(
                    "Data Quality After Cleaning",
                    class_name="text-lg font-semibold text-gray-800 mb-4",
                ),
                rx.el.div(
                    data_quality_card(
                        title="Total Rows",
                        value=DataCleaningState.cleaned_rows,
                        unit="",
                        icon="rows",
                    ),
                    data_quality_card(
                        title="Missing Values",
                        value=DataCleaningState.missing_values_after,
                        unit="",
                        icon="circle-check",
                    ),
                    data_quality_card(
                        title="Outliers Handled",
                        value=DataCleaningState.outliers_after,
                        unit=" (Capped)",
                        icon="shield-check",
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-3 gap-4",
                ),
                class_name="p-6 bg-blue-50 rounded-2xl border border-blue-200",
            ),
            class_name="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8",
        ),
        rx.el.h3(
            "Correlation Heatmap (Cleaned Data)",
            class_name="text-xl font-semibold text-gray-800 mb-4",
        ),
        rx.el.div(
            rx.image(
                src=rx.get_upload_url(DataCleaningState.correlation_heatmap),
                class_name="rounded-lg shadow-md w-full",
            ),
            class_name="p-6 bg-white rounded-2xl border border-gray-200 flex justify-center items-center",
        ),
        rx.el.div(
            rx.el.a(
                rx.el.button(
                    "Proceed to PCA Analysis",
                    rx.icon("arrow-right", class_name="ml-2 h-5 w-5"),
                    class_name="inline-flex items-center justify-center rounded-xl bg-blue-600 px-6 py-3 text-base font-semibold text-white shadow-sm hover:bg-blue-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 transition-transform hover:scale-105",
                ),
                href="/pca-analysis",
            ),
            class_name="w-full flex justify-end mt-8",
        ),
        class_name="w-full",
    )


def data_cleaning() -> rx.Component:
    return rx.el.div(
        rx.el.h1(
            "1. Upload and Clean Customer Data",
            class_name="text-3xl font-bold text-gray-900",
        ),
        rx.el.p(
            "Begin by uploading your bank customer dataset in CSV format.",
            class_name="mt-2 text-lg text-gray-600 mb-10",
        ),
        rx.cond(
            DataCleaningState.uploaded_file == "",
            upload_component(),
            rx.el.div(
                uploaded_data_view(),
                rx.cond(
                    DataCleaningState.is_cleaning,
                    rx.el.div(
                        rx.spinner(size="3"),
                        rx.el.p(
                            "Cleaning data... this may take a moment.",
                            class_name="mt-4 text-gray-600",
                        ),
                        class_name="flex flex-col items-center justify-center p-12 bg-gray-50/80 rounded-lg w-full mt-8",
                    ),
                    rx.cond(
                        DataCleaningState.cleaning_done,
                        cleaning_results_view(),
                        rx.fragment(),
                    ),
                ),
                class_name="w-full flex flex-col items-center",
            ),
        ),
        class_name="p-6 sm:p-10 w-full max-w-7xl mx-auto",
    )