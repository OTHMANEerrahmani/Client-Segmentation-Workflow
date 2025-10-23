import reflex as rx
from app.states.pca_state import PCAState
from app.states.data_cleaning_state import DataCleaningState
from app.states.clustering_state import ClusteringState, CLUSTER_COLORS


def metric_card(title: str, value: rx.Var, unit: str = "") -> rx.Component:
    return rx.el.div(
        rx.el.p(title, class_name="text-sm font-medium text-gray-500"),
        rx.el.p(value, unit, class_name="text-2xl font-semibold text-gray-900"),
        class_name="p-4 bg-white rounded-xl border border-gray-200 shadow-sm text-center",
    )


def cluster_scatter_plot() -> rx.Component:
    return rx.recharts.scatter_chart(
        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
        rx.recharts.x_axis(data_key="x", type_="number", name="PC1"),
        rx.recharts.y_axis(data_key="y", type_="number", name="PC2"),
        rx.recharts.tooltip(),
        rx.foreach(
            ClusteringState.get_scatter_data_for_cluster,
            lambda data, index: rx.recharts.scatter(
                data=data,
                fill=rx.Var.create(CLUSTER_COLORS)[index % len(CLUSTER_COLORS)],
                name=f"Cluster {index}",
            ),
        ),
        height=400,
        width="100%",
    )


def algorithm_selector() -> rx.Component:
    return rx.el.div(
        rx.el.p(
            "Select Clustering Algorithm:",
            class_name="font-semibold text-gray-700 mb-2",
        ),
        rx.el.div(
            rx.foreach(
                ["KMeans", "Hierarchical"],
                lambda algo: rx.el.button(
                    algo,
                    on_click=ClusteringState.set_selected_algorithm(algo),
                    class_name=rx.cond(
                        ClusteringState.selected_algorithm == algo,
                        "px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold",
                        "px-4 py-2 rounded-lg bg-gray-200 text-gray-700 hover:bg-gray-300",
                    ),
                ),
            ),
            class_name="flex gap-4",
        ),
        class_name="mb-6",
    )


def clustering_controls() -> rx.Component:
    return rx.el.div(
        algorithm_selector(),
        rx.el.div(
            rx.el.p(
                f"Number of Clusters (k): {ClusteringState.n_clusters}",
                class_name="font-medium",
            ),
            rx.el.input(
                type="range",
                min=2,
                max=10,
                key=f"n_clusters_slider_{ClusteringState.n_clusters}",
                default_value=ClusteringState.n_clusters.to_string(),
                on_change=ClusteringState.set_n_clusters.throttle(100),
                class_name="w-64",
            ),
            class_name="flex items-center gap-4 mb-6",
        ),
        rx.el.button(
            "Run Clustering",
            on_click=ClusteringState.run_clustering,
            is_loading=ClusteringState.is_running_clustering,
            class_name="inline-flex items-center justify-center rounded-xl bg-blue-600 px-8 py-4 text-lg font-semibold text-white shadow-sm hover:bg-blue-700 transition-transform hover:scale-105",
        ),
        class_name="flex flex-col items-center p-8 bg-gray-50 rounded-2xl border border-gray-200",
    )


def clustering_results() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Clustering Results", class_name="text-2xl font-bold text-gray-900 mb-6"
        ),
        rx.el.div(
            metric_card("KMeans Silhouette", ClusteringState.kmeans_silhouette, ""),
            metric_card(
                "Hierarchical Silhouette", ClusteringState.hierarchical_silhouette, ""
            ),
            metric_card("KMeans Clusters", ClusteringState.kmeans_clusters, ""),
            metric_card(
                "Hierarchical Clusters", ClusteringState.hierarchical_clusters, ""
            ),
            class_name="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    f"PCA Scatter Plot ({ClusteringState.selected_algorithm})",
                    class_name="text-lg font-semibold text-gray-800 mb-4",
                ),
                cluster_scatter_plot(),
                class_name="p-6 bg-white rounded-2xl border border-gray-200",
            ),
            rx.el.div(
                rx.el.h3(
                    "Hierarchical Clustering Dendrogram",
                    class_name="text-lg font-semibold text-gray-800 mb-4",
                ),
                rx.image(
                    src=rx.get_upload_url(ClusteringState.dendrogram_image),
                    class_name="rounded-lg shadow-md w-full",
                ),
                class_name="p-6 bg-white rounded-2xl border border-gray-200",
            ),
            class_name="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8",
        ),
        rx.el.div(
            rx.el.a(
                rx.el.button(
                    "Generate Customer Profiles",
                    rx.icon("arrow-right", class_name="ml-2 h-5 w-5"),
                    class_name="inline-flex items-center justify-center rounded-xl bg-blue-600 px-6 py-3 text-base font-semibold text-white shadow-sm hover:bg-blue-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 transition-transform hover:scale-105",
                ),
                href="/customer-profiles",
            ),
            class_name="w-full flex justify-end mt-8",
        ),
        class_name="w-full",
    )


def clustering_page() -> rx.Component:
    return rx.el.div(
        rx.el.h1(
            "3. Customer Clustering", class_name="text-3xl font-bold text-gray-900"
        ),
        rx.el.p(
            "Group customers into meaningful segments using different clustering algorithms.",
            class_name="mt-2 text-lg text-gray-600 mb-10",
        ),
        rx.cond(
            ~PCAState.pca_done,
            rx.el.div(
                rx.icon("flag_triangle_right", class_name="h-12 w-12 text-yellow-500"),
                rx.el.p(
                    "Please complete the PCA step first.",
                    class_name="mt-4 font-semibold text-gray-700",
                ),
                rx.el.a(
                    "Go to PCA Analysis",
                    href="/pca-analysis",
                    class_name="mt-4 text-blue-600 underline",
                ),
                class_name="flex flex-col items-center justify-center p-12 bg-yellow-50 border border-yellow-200 rounded-xl",
            ),
            rx.el.div(
                rx.cond(
                    ClusteringState.is_running_clustering,
                    rx.el.div(
                        rx.spinner(size="3"),
                        rx.el.p(
                            "Running clustering...", class_name="mt-4 text-gray-600"
                        ),
                        class_name="flex flex-col items-center justify-center p-12 bg-gray-50/80 rounded-lg w-full mt-8",
                    ),
                    rx.cond(
                        ClusteringState.clustering_done,
                        clustering_results(),
                        clustering_controls(),
                    ),
                ),
                class_name="w-full flex flex-col items-center",
            ),
        ),
        class_name="p-6 sm:p-10 w-full max-w-7xl mx-auto",
    )