import reflex as rx
from app.state import WebAppState


def workflow_step_indicator(step: dict) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.cond(
                step["status"] == "completed",
                rx.icon("check", class_name="h-5 w-5 text-white"),
                rx.el.div(class_name="h-2.5 w-2.5 rounded-full bg-gray-300"),
            ),
            class_name=rx.cond(
                step["status"] == "completed",
                "flex h-10 w-10 items-center justify-center rounded-full bg-blue-600",
                "flex h-10 w-10 items-center justify-center rounded-full bg-gray-100 border border-gray-200",
            ),
        ),
        rx.el.p(
            step["name"],
            class_name=rx.cond(
                step["status"] == "completed",
                "mt-2 text-sm font-semibold text-gray-800",
                "mt-2 text-sm font-medium text-gray-500",
            ),
        ),
        class_name="flex flex-col items-center",
    )


def feature_card_component(card: dict) -> rx.Component:
    return rx.el.div(
        rx.icon(card["icon"], class_name="h-8 w-8 mb-4 text-blue-600"),
        rx.el.h3(card["title"], class_name="text-lg font-semibold text-gray-900 mb-2"),
        rx.el.p(card["description"], class_name="text-sm text-gray-600 text-center"),
        class_name="flex flex-col items-center justify-start p-6 bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-300 w-full",
    )


def home_page() -> rx.Component:
    return rx.el.div(
        rx.el.h1(
            "Customer Segmentation Analysis",
            class_name="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl",
        ),
        rx.el.p(
            "An end-to-end platform for uploading, cleaning, and analyzing customer data to uncover valuable segments.",
            class_name="mt-4 max-w-2xl text-lg text-gray-600",
        ),
        rx.el.div(
            rx.foreach(WebAppState.pipeline_steps, workflow_step_indicator),
            class_name="mt-16 mb-12 flex items-center justify-center space-x-8 md:space-x-16 relative",
        ),
        rx.el.a(
            rx.el.button(
                "Get Started",
                rx.icon("arrow-right", class_name="ml-2 h-5 w-5"),
                class_name="inline-flex items-center justify-center rounded-xl bg-blue-600 px-8 py-4 text-base font-semibold text-white shadow-sm hover:bg-blue-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600 transition-transform hover:scale-105",
            ),
            href="/data-cleaning",
            on_click=lambda: WebAppState.set_active_page("Data Cleaning"),
        ),
        rx.el.div(
            rx.foreach(WebAppState.feature_cards, feature_card_component),
            class_name="mt-20 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5",
        ),
        class_name="flex flex-col items-center text-center p-6 sm:p-10",
    )