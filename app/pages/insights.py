import reflex as rx
from app.states.customer_profile_state import CustomerProfileState
from app.states.insights_state import InsightsState


def kpi_card(kpi: dict) -> rx.Component:
    return rx.el.div(
        rx.icon(kpi["icon"], class_name="h-8 w-8 text-blue-600"),
        rx.el.div(
            rx.el.p(kpi["title"], class_name="text-sm font-medium text-gray-500"),
            rx.el.p(kpi["value"], class_name="text-3xl font-bold text-gray-900"),
            class_name="ml-4",
        ),
        class_name="flex items-center p-6 bg-white rounded-2xl border border-gray-100 shadow-sm",
    )


def pie_chart() -> rx.Component:
    return rx.recharts.pie_chart(
        rx.recharts.pie(
            data=InsightsState.segment_distribution,
            data_key="value",
            name_key="name",
            cx="50%",
            cy="50%",
            outer_radius=120,
            label_line=False,
            stroke="#fff",
            stroke_width=2,
        ),
        rx.recharts.tooltip(),
        width="100%",
        height=400,
    )


def recommendation_item(rec: dict) -> rx.Component:
    return rx.el.div(
        rx.icon(rec["icon"], class_name="h-5 w-5 text-gray-500"),
        rx.el.p(rec["text"], class_name="text-sm text-gray-700 ml-3"),
        class_name="flex items-center",
    )


def insight_card(insight: dict) -> rx.Component:
    return rx.el.div(
        rx.el.h3(f"{insight['label']}", class_name="text-xl font-bold text-gray-900"),
        rx.el.p(
            f"{insight['count']} Customers ({insight['percentage']:.1f}%)",
            class_name="text-sm font-medium text-gray-500 mb-4",
        ),
        rx.el.h4("Top KPIs", class_name="text-md font-semibold text-gray-700 mb-2"),
        rx.el.div(
            rx.el.p(f"Avg. Income: €{insight['avg_income']:.2f}", class_name="text-sm"),
            rx.el.p(
                f"Avg. Savings: €{insight['avg_savings']:.2f}", class_name="text-sm"
            ),
            rx.el.p(
                f"Avg. Spend: €{insight['avg_spending']:.2f}", class_name="text-sm"
            ),
            class_name="grid grid-cols-3 gap-2 mb-4 p-3 bg-gray-50 rounded-lg",
        ),
        rx.el.h4(
            "Marketing Recommendations",
            class_name="text-md font-semibold text-gray-700 mb-3",
        ),
        rx.el.div(
            rx.foreach(insight["recommendations"], recommendation_item),
            class_name="flex flex-col gap-2",
        ),
        class_name="p-6 rounded-2xl border shadow-sm",
        style={
            "border-color": insight["color"],
            "background-color": f"{insight['color']}10",
        },
    )


def insights_view() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Marketing Insights Dashboard",
            class_name="text-2xl font-bold text-gray-900 mb-2",
        ),
        rx.el.p(
            "Actionable recommendations for each customer segment.",
            class_name="text-gray-600 mb-8",
        ),
        rx.el.div(
            rx.foreach(InsightsState.kpis, kpi_card),
            class_name="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12",
        ),
        rx.el.div(
            rx.el.h3(
                "Segment Distribution",
                class_name="text-xl font-semibold text-gray-800 mb-4",
            ),
            pie_chart(),
            class_name="p-6 bg-white rounded-2xl border border-gray-200 shadow-sm mb-12",
        ),
        rx.el.div(
            rx.foreach(InsightsState.segment_insights, insight_card),
            class_name="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8",
        ),
        rx.el.div(
            rx.el.button(
                "Download PDF Report",
                rx.icon("file-text", class_name="mr-2"),
                class_name="inline-flex items-center rounded-lg bg-gray-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-gray-700",
                on_click=rx.toast.info("PDF export coming soon!"),
            ),
            rx.el.button(
                "Export Full Data (CSV)",
                rx.icon("download", class_name="mr-2"),
                class_name="inline-flex items-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-700",
                on_click=CustomerProfileState.download_segmented_data,
            ),
            class_name="flex justify-end gap-4 mt-8",
        ),
        class_name="w-full",
    )


def insights_page() -> rx.Component:
    return rx.el.div(
        rx.el.h1(
            "5. AI-Powered Insights", class_name="text-3xl font-bold text-gray-900"
        ),
        rx.el.p(
            "Automated analysis and marketing recommendations for your customer segments.",
            class_name="mt-2 text-lg text-gray-600 mb-10",
        ),
        rx.cond(
            ~CustomerProfileState.profiles_generated,
            rx.el.div(
                rx.icon("flag-triangle-right", class_name="h-12 w-12 text-yellow-500"),
                rx.el.p(
                    "Please generate customer profiles first.",
                    class_name="mt-4 font-semibold text-gray-700",
                ),
                rx.el.a(
                    "Go to Customer Profiles",
                    href="/customer-profiles",
                    class_name="mt-4 text-blue-600 underline",
                ),
                class_name="flex flex-col items-center justify-center p-12 bg-yellow-50 border border-yellow-200 rounded-xl",
            ),
            rx.el.div(
                rx.cond(
                    ~InsightsState.insights_generated,
                    rx.el.div(
                        rx.el.button(
                            "Generate AI Insights",
                            on_click=InsightsState.generate_insights,
                            is_loading=InsightsState.is_generating,
                            class_name="inline-flex items-center justify-center rounded-xl bg-blue-600 px-8 py-4 text-lg font-semibold text-white shadow-sm hover:bg-blue-700 transition-transform hover:scale-105",
                        ),
                        class_name="w-full flex justify-center py-16",
                    ),
                    insights_view(),
                ),
                rx.cond(
                    InsightsState.is_generating,
                    rx.el.div(
                        rx.spinner(size="3"),
                        rx.el.p(
                            "Generating insights... this can take a moment.",
                            class_name="mt-4 text-gray-600",
                        ),
                        class_name="flex flex-col items-center justify-center p-12 bg-gray-50/80 rounded-lg w-full mt-8",
                    ),
                    rx.fragment(),
                ),
                class_name="w-full flex flex-col items-center",
            ),
        ),
        class_name="p-6 sm:p-10 w-full max-w-7xl mx-auto",
    )