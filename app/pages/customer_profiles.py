import reflex as rx
from app.states.clustering_state import ClusteringState
from app.states.customer_profile_state import CustomerProfileState


def feature_display(feature: dict) -> rx.Component:
    return rx.el.div(
        rx.el.p(feature["feature"], class_name="text-sm font-medium text-gray-600"),
        rx.el.p(
            f"{feature['value']}", class_name="text-lg font-semibold text-blue-600"
        ),
        class_name="flex justify-between items-baseline",
    )


def segment_profile_card(profile: dict) -> rx.Component:
    return rx.el.div(
        rx.el.h3(profile["label"], class_name="text-xl font-bold text-gray-900 mb-2"),
        rx.el.div(
            rx.el.p(
                f"{profile['count']} Customers",
                class_name="text-sm font-medium text-gray-500",
            ),
            rx.el.span(
                f"({profile['percentage']:.1f}% of total)",
                class_name="text-sm font-medium text-green-600 bg-green-100 px-2 py-1 rounded-full",
            ),
            class_name="flex items-center gap-2 mb-4",
        ),
        rx.el.p(
            "Top Distinguishing Features:",
            class_name="text-md font-semibold text-gray-700 mb-3",
        ),
        rx.el.div(
            rx.foreach(profile["top_features"], feature_display),
            class_name="flex flex-col gap-2",
        ),
        class_name="p-6 bg-white rounded-2xl border border-gray-200 shadow-sm w-full",
    )


def summary_stats_table() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Cluster Summary Statistics (Mean Values)",
            class_name="text-2xl font-bold text-gray-900 mb-6",
        ),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.foreach(
                            CustomerProfileState.cluster_summary_columns,
                            lambda col: rx.el.th(
                                col.replace("_", " ").title(),
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                            ),
                        )
                    )
                ),
                rx.el.tbody(
                    rx.foreach(
                        CustomerProfileState.cluster_summary_stats,
                        lambda row: rx.el.tr(
                            rx.foreach(
                                CustomerProfileState.cluster_summary_columns,
                                lambda col: rx.el.td(
                                    row[col].to_string(),
                                    class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-700 font-mono",
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
        ),
    )


def profiles_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Customer Segment Profiles",
                class_name="text-2xl font-bold text-gray-900",
            ),
            rx.el.div(
                rx.el.button(
                    "Export Segments (CSV)",
                    rx.icon("download", class_name="ml-2 h-4 w-4"),
                    on_click=CustomerProfileState.download_segmented_data,
                    class_name="inline-flex items-center rounded-lg bg-gray-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-gray-700",
                ),
                rx.el.a(
                    rx.el.button(
                        "Generate Insights",
                        rx.icon("arrow-right", class_name="ml-2 h-5 w-5"),
                        class_name="inline-flex items-center justify-center rounded-xl bg-blue-600 px-6 py-3 text-base font-semibold text-white shadow-sm hover:bg-blue-700 transition-transform hover:scale-105",
                    ),
                    href="/insights",
                ),
                class_name="flex items-center gap-4",
            ),
            class_name="flex justify-between items-center w-full mb-8",
        ),
        rx.el.div(
            rx.foreach(CustomerProfileState.segment_profiles, segment_profile_card),
            class_name="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12",
        ),
        summary_stats_table(),
        class_name="w-full",
    )


def customer_profiles_page() -> rx.Component:
    return rx.el.div(
        rx.el.h1(
            "4. Customer Segment Profiles",
            class_name="text-3xl font-bold text-gray-900",
        ),
        rx.el.p(
            "Detailed analysis of each customer segment based on the clustering results.",
            class_name="mt-2 text-lg text-gray-600 mb-10",
        ),
        rx.cond(
            ~ClusteringState.clustering_done,
            rx.el.div(
                rx.icon("flag-triangle-right", class_name="h-12 w-12 text-yellow-500"),
                rx.el.p(
                    "Please complete the clustering step first.",
                    class_name="mt-4 font-semibold text-gray-700",
                ),
                rx.el.a(
                    "Go to Clustering",
                    href="/clustering",
                    class_name="mt-4 text-blue-600 underline",
                ),
                class_name="flex flex-col items-center justify-center p-12 bg-yellow-50 border border-yellow-200 rounded-xl",
            ),
            rx.el.div(
                rx.cond(
                    ~CustomerProfileState.profiles_generated,
                    rx.el.div(
                        rx.el.button(
                            "Generate Customer Profiles",
                            on_click=CustomerProfileState.generate_profiles,
                            is_loading=CustomerProfileState.is_generating,
                            class_name="inline-flex items-center justify-center rounded-xl bg-blue-600 px-8 py-4 text-lg font-semibold text-white shadow-sm hover:bg-blue-700 transition-transform hover:scale-105",
                        ),
                        class_name="w-full flex justify-center py-16",
                    ),
                    profiles_view(),
                ),
                rx.el.div(
                    rx.cond(
                        CustomerProfileState.is_generating,
                        rx.el.div(
                            rx.spinner(size="3"),
                            rx.el.p(
                                "Generating profiles...",
                                class_name="mt-4 text-gray-600",
                            ),
                            class_name="flex flex-col items-center justify-center p-12 bg-gray-50/80 rounded-lg w-full mt-8",
                        ),
                        rx.fragment(),
                    ),
                    class_name="w-full flex flex-col items-center",
                ),
            ),
        ),
        class_name="p-6 sm:p-10 w-full max-w-7xl mx-auto",
    )