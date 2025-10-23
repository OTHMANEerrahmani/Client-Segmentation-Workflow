import reflex as rx
from app.state import WebAppState


def nav_item(item: dict, active: bool) -> rx.Component:
    return rx.el.a(
        rx.el.div(
            rx.icon(item["icon"], class_name="h-5 w-5"),
            rx.el.span(item["name"]),
            class_name=rx.cond(
                active,
                "flex items-center gap-3 rounded-lg bg-blue-100 px-3 py-2 text-blue-600 transition-all hover:text-blue-700 font-semibold",
                "flex items-center gap-3 rounded-lg px-3 py-2 text-gray-500 transition-all hover:text-gray-900",
            ),
        ),
        href=item["path"],
        on_click=lambda: WebAppState.set_active_page(item["name"]),
    )


def sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.el.a(
                    rx.icon("wallet-minimal", class_name="h-8 w-8 text-blue-600"),
                    rx.el.span(
                        "Client Segmentation",
                        class_name="text-lg font-semibold text-gray-800",
                    ),
                    href="/",
                    class_name="flex items-center gap-2",
                ),
                class_name="flex h-16 items-center border-b px-6 shrink-0",
            ),
            rx.el.nav(
                rx.foreach(
                    WebAppState.nav_items,
                    lambda item: nav_item(
                        item, WebAppState.active_page == item["name"]
                    ),
                ),
                class_name="flex flex-col gap-1 p-4",
            ),
            class_name="flex-1 overflow-auto",
        ),
        rx.el.div(
            rx.el.p("© 2024 Banking Analytics", class_name="text-xs text-gray-500"),
            class_name="mt-auto p-4 border-t",
        ),
        class_name="hidden md:flex flex-col w-64 border-r bg-gray-50/50 h-screen",
    )