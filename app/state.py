import reflex as rx
from typing import TypedDict


class NavItem(TypedDict):
    name: str
    path: str
    icon: str


class WorkflowStep(TypedDict):
    name: str
    status: str


class FeatureCard(TypedDict):
    icon: str
    title: str
    description: str


from app.states.data_cleaning_state import DataCleaningState
from app.states.pca_state import PCAState
from app.states.clustering_state import ClusteringState
from app.states.customer_profile_state import CustomerProfileState
from app.states.insights_state import InsightsState


class WebAppState(rx.State):
    active_page: str = "Home"

    @rx.var
    async def pipeline_steps(self) -> list[WorkflowStep]:
        data_cleaning_state = await self.get_state(DataCleaningState)
        pca_state = await self.get_state(PCAState)
        clustering_state = await self.get_state(ClusteringState)
        steps = [
            {
                "name": "Upload",
                "status": "completed"
                if data_cleaning_state.uploaded_file
                else "pending",
            },
            {
                "name": "Cleaning",
                "status": "completed"
                if data_cleaning_state.cleaning_done
                else "pending",
            },
            {"name": "PCA", "status": "completed" if pca_state.pca_done else "pending"},
            {
                "name": "Clustering",
                "status": "completed"
                if clustering_state.clustering_done
                else "pending",
            },
            {
                "name": "Profiles",
                "status": "completed"
                if (await self.get_state(CustomerProfileState)).profiles_generated
                else "pending",
            },
            {
                "name": "Insights",
                "status": "completed"
                if (await self.get_state(InsightsState)).insights_generated
                else "pending",
            },
        ]
        return steps

    nav_items: list[NavItem] = [
        {"name": "Home", "path": "/", "icon": "home"},
        {"name": "Data Cleaning", "path": "/data-cleaning", "icon": "filter"},
        {"name": "PCA Analysis", "path": "/pca-analysis", "icon": "bar-chart-2"},
        {"name": "Clustering", "path": "/clustering", "icon": "layout-grid"},
        {"name": "Customer Profiles", "path": "/customer-profiles", "icon": "users"},
        {"name": "Insights", "path": "/insights", "icon": "lightbulb"},
    ]
    feature_cards: list[FeatureCard] = [
        {
            "icon": "upload-cloud",
            "title": "1. Upload Data",
            "description": "Securely upload your customer data in CSV or Excel format.",
        },
        {
            "icon": "sparkles",
            "title": "2. Automated Cleaning",
            "description": "Our pipeline automatically handles missing values, outliers, and normalization.",
        },
        {
            "icon": "bar-chart-big",
            "title": "3. PCA Analysis",
            "description": "Reduce dimensionality and discover the most important features driving variance.",
        },
        {
            "icon": "brain-circuit",
            "title": "4. Clustering",
            "description": "Apply KMeans and Hierarchical clustering to group customers into meaningful segments.",
        },
        {
            "icon": "lightbulb",
            "title": "5. AI-Powered Insights",
            "description": "Get automated explanations and marketing recommendations for each customer segment.",
        },
    ]

    @rx.event
    def set_active_page(self, page_name: str):
        self.active_page = page_name