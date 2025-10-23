import reflex as rx
from app.states.data_cleaning_state import DataCleaningState
from app.states.pca_state import PCAState


def chart_card(title: str, chart: rx.Component) -> rx.Component:
    return rx.el.div(
        rx.el.h3(title, class_name="text-lg font-semibold text-gray-800 mb-4"),
        rx.el.div(chart, class_name="p-4 bg-white rounded-xl border border-gray-200"),
        class_name="w-full",
    )


def scree_plot_chart() -> rx.Component:
    return rx.recharts.bar_chart(
        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
        rx.recharts.bar(data_key="variance", fill="#3b82f6"),
        rx.recharts.x_axis(data_key="component"),
        rx.recharts.y_axis(
            rx.recharts.label(
                value="Explained Variance", angle=-90, position="insideLeft"
            )
        ),
        rx.recharts.tooltip(),
        data=PCAState.scree_plot_data,
        height=300,
    )


def cumulative_variance_chart() -> rx.Component:
    return rx.recharts.line_chart(
        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
        rx.recharts.line(
            data_key="cumulative_variance", stroke="#10b981", type_="monotone"
        ),
        rx.recharts.x_axis(data_key="component"),
        rx.recharts.y_axis(
            rx.recharts.label(
                value="Cumulative Variance", angle=-90, position="insideLeft"
            ),
            domain=[0, 1],
        ),
        rx.recharts.tooltip(),
        rx.recharts.reference_line(
            y="0.8", label="80% Threshold", stroke="#ef4444", stroke_dasharray="3 3"
        ),
        data=PCAState.cumulative_variance_data,
        height=300,
    )


def component_contribution_table() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Component Contributions (Top 5 Features)",
            class_name="text-lg font-semibold text-gray-800 mb-4",
        ),
        rx.el.div(
            rx.foreach(
                PCAState.component_contributions,
                lambda comp: rx.el.div(
                    rx.el.h4(
                        comp["component"], class_name="font-semibold text-gray-700 mb-2"
                    ),
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                rx.el.th("Feature", class_name="text-left"),
                                rx.el.th("Loading", class_name="text-right"),
                            )
                        ),
                        rx.el.tbody(
                            rx.foreach(
                                comp["features"],
                                lambda feature: rx.el.tr(
                                    rx.el.td(feature["name"]),
                                    rx.el.td(
                                        rx.el.span(f"{feature['value']:.3f}"),
                                        class_name="text-right font-mono",
                                    ),
                                ),
                            )
                        ),
                        class_name="w-full text-sm",
                    ),
                    class_name="p-4 bg-white rounded-xl border border-gray-200",
                ),
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4",
        ),
        class_name="w-full",
    )


def pca_results_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    "Components Selected",
                    class_name="text-sm font-medium text-gray-500",
                ),
                rx.el.p(
                    PCAState.n_components, class_name="text-3xl font-bold text-blue-600"
                ),
                class_name="p-6 text-center bg-blue-50 border border-blue-200 rounded-xl",
            ),
            rx.el.div(
                rx.el.p(
                    "Explained Variance", class_name="text-sm font-medium text-gray-500"
                ),
                rx.el.p(
                    rx.cond(
                        PCAState.cumulative_variance.length() > 0,
                        f"{(PCAState.cumulative_variance[-1] * 100).to_string()}%",
                        "0.00%",
                    ),
                    class_name="text-3xl font-bold text-green-600",
                ),
                class_name="p-6 text-center bg-green-50 border border-green-200 rounded-xl",
            ),
            class_name="grid grid-cols-2 gap-6 mb-8",
        ),
        rx.el.p(
            PCAState.pca_summary,
            class_name="mb-8 p-4 bg-gray-100 rounded-lg text-gray-700",
        ),
        rx.el.div(
            chart_card(
                "Scree Plot (Explained Variance per Component)", scree_plot_chart()
            ),
            chart_card("Cumulative Explained Variance", cumulative_variance_chart()),
            class_name="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8",
        ),
        component_contribution_table(),
        rx.el.div(
            rx.el.a(
                rx.el.button(
                    "Proceed to Clustering",
                    rx.icon("arrow-right", class_name="ml-2 h-5 w-5"),
                    class_name="inline-flex items-center justify-center rounded-xl bg-blue-600 px-6 py-3 text-base font-semibold text-white shadow-sm hover:bg-blue-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 transition-transform hover:scale-105",
                ),
                href="/clustering",
            ),
            class_name="w-full flex justify-end mt-8",
        ),
        class_name="w-full",
    )


def pca_analysis_page() -> rx.Component:
    return rx.el.div(
        rx.el.h1(
            "2. Principal Component Analysis (PCA)",
            class_name="text-3xl font-bold text-gray-900",
        ),
        rx.el.p(
            "Reduce data dimensionality and identify key features driving variance.",
            class_name="mt-2 text-lg text-gray-600 mb-10",
        ),
        rx.cond(
            ~DataCleaningState.cleaning_done,
            rx.el.div(
                rx.icon("flag_triangle_right", class_name="h-12 w-12 text-yellow-500"),
                rx.el.p(
                    "Please complete the data cleaning step first.",
                    class_name="mt-4 font-semibold text-gray-700",
                ),
                rx.el.a(
                    "Go to Data Cleaning",
                    href="/data-cleaning",
                    class_name="mt-4 text-blue-600 underline",
                ),
                class_name="flex flex-col items-center justify-center p-12 bg-yellow-50 border border-yellow-200 rounded-xl",
            ),
            rx.el.div(
                rx.cond(
                    ~PCAState.pca_done & ~PCAState.is_running_pca,
                    rx.el.div(
                        rx.el.button(
                            "Start PCA Analysis",
                            on_click=PCAState.run_pca,
                            class_name="inline-flex items-center justify-center rounded-xl bg-blue-600 px-8 py-4 text-lg font-semibold text-white shadow-sm hover:bg-blue-700 transition-transform hover:scale-105",
                        ),
                        class_name="w-full flex justify-center py-16",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    PCAState.is_running_pca,
                    rx.el.div(
                        rx.spinner(size="3"),
                        rx.el.p(
                            "Running PCA... this may take a moment.",
                            class_name="mt-4 text-gray-600",
                        ),
                        class_name="flex flex-col items-center justify-center p-12 bg-gray-50/80 rounded-lg w-full mt-8",
                    ),
                    rx.cond(PCAState.pca_done, pca_results_view(), rx.fragment()),
                ),
                class_name="w-full flex flex-col items-center",
            ),
        ),
        class_name="p-6 sm:p-10 w-full max-w-7xl mx-auto",
    )