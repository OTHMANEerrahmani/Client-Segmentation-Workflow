import reflex as rx
from app.state import WebAppState
from app.components.sidebar import sidebar
from app.pages.home import home_page
from app.pages.data_cleaning import data_cleaning as data_cleaning_page


def page_layout(content: rx.Component) -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.main(content, class_name="flex-1 h-screen overflow-y-auto bg-gray-50"),
        class_name="flex min-h-screen w-full bg-white font-['Inter']",
    )


def index() -> rx.Component:
    return page_layout(home_page())


def data_cleaning() -> rx.Component:
    return page_layout(data_cleaning_page())


from app.pages.pca_analysis import pca_analysis_page


def pca_analysis() -> rx.Component:
    return page_layout(pca_analysis_page())


from app.pages.clustering import clustering_page


def clustering() -> rx.Component:
    return page_layout(clustering_page())


from app.pages.customer_profiles import customer_profiles_page


def customer_profiles() -> rx.Component:
    return page_layout(customer_profiles_page())


from app.pages.insights import insights_page


def insights() -> rx.Component:
    return page_layout(insights_page())


from app.states.data_cleaning_state import DataCleaningState

app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, on_load=WebAppState.set_active_page("Home"))
app.add_page(
    data_cleaning,
    route="/data-cleaning",
    on_load=WebAppState.set_active_page("Data Cleaning"),
)
app.add_page(
    pca_analysis,
    route="/pca-analysis",
    on_load=WebAppState.set_active_page("PCA Analysis"),
)
app.add_page(
    clustering, route="/clustering", on_load=WebAppState.set_active_page("Clustering")
)
app.add_page(
    customer_profiles,
    route="/customer-profiles",
    on_load=WebAppState.set_active_page("Customer Profiles"),
)
app.add_page(
    insights, route="/insights", on_load=WebAppState.set_active_page("Insights")
)