import reflex as rx
import pandas as pd
import numpy as np
import io
from typing import TypedDict
import logging
from app.states.customer_profile_state import CustomerProfileState, SegmentProfile


class KpiData(TypedDict):
    title: str
    value: str
    icon: str


class MarketingRec(TypedDict):
    text: str
    icon: str


class SegmentInsight(TypedDict):
    label: str
    count: int
    percentage: float
    color: str
    avg_income: float
    avg_savings: float
    avg_spending: float
    recommendations: list[MarketingRec]


INSIGHT_COLORS = ["#3b82f6", "#10b981", "#f97316", "#8b5cf6", "#ec4899", "#ef4444"]


class InsightsState(rx.State):
    insights_generated: bool = False
    is_generating: bool = False
    kpis: list[KpiData] = []
    segment_distribution: list[dict] = []
    segment_insights: list[SegmentInsight] = []

    def _get_recommendations(self, profile: SegmentProfile) -> list[MarketingRec]:
        recs = []
        label = profile["label"].lower()
        top_features = [f["feature"].lower() for f in profile["top_features"]]
        if "high-income" in label or "monthly income" in " ".join(top_features):
            recs.append(
                {
                    "text": "Promote premium credit cards and investment services.",
                    "icon": "gem",
                }
            )
        if "premium savers" in label or "savings amount" in " ".join(top_features):
            recs.append(
                {
                    "text": "Offer high-yield savings accounts and financial advisory.",
                    "icon": "piggy-bank",
                }
            )
        if "monthly card spending" in " ".join(top_features):
            recs.append(
                {
                    "text": "Introduce loyalty programs and cashback offers.",
                    "icon": "gift",
                }
            )
        if len(recs) < 3:
            if profile["percentage"] > 25:
                recs.append(
                    {
                        "text": "Launch targeted digital marketing campaigns.",
                        "icon": "megaphone",
                    }
                )
            if len(recs) < 3:
                recs.append(
                    {
                        "text": "Personalize email communication with relevant offers.",
                        "icon": "mail",
                    }
                )
            if len(recs) < 3:
                recs.append(
                    {
                        "text": "Conduct surveys to gather more specific feedback.",
                        "icon": "message-square-quote",
                    }
                )
        return recs[:3]

    @rx.event(background=True)
    async def generate_insights(self):
        async with self:
            self.is_generating = True
            yield
        try:
            async with self:
                profile_state = await self.get_state(CustomerProfileState)
            if not profile_state.profiles_generated:
                yield rx.toast.error("Customer profiles are not generated yet.")
                async with self:
                    self.is_generating = False
                return
            total_customers = sum((p["count"] for p in profile_state.segment_profiles))
            num_segments = len(profile_state.segment_profiles)
            avg_segment_size = total_customers / num_segments if num_segments > 0 else 0
            kpis = [
                {
                    "title": "Total Customers",
                    "value": str(total_customers),
                    "icon": "users",
                },
                {
                    "title": "Segments Identified",
                    "value": str(num_segments),
                    "icon": "brain-circuit",
                },
                {
                    "title": "Avg. Segment Size",
                    "value": str(int(avg_segment_size)),
                    "icon": "users-round",
                },
            ]
            dist_data = []
            insights_data = []
            for i, profile in enumerate(profile_state.segment_profiles):
                color = INSIGHT_COLORS[i % len(INSIGHT_COLORS)]
                dist_data.append(
                    {"name": profile["label"], "value": profile["count"], "fill": color}
                )
                summary = next(
                    (
                        s
                        for s in profile_state.cluster_summary_stats
                        if s["cluster"] == profile["cluster_id"]
                    ),
                    None,
                )
                avg_income = summary.get("Monthly Income (€)", 0) if summary else 0
                avg_savings = summary.get("Savings Amount (€)", 0) if summary else 0
                avg_spending = (
                    summary.get("Monthly Card Spending (€)", 0) if summary else 0
                )
                insights_data.append(
                    {
                        "label": profile["label"],
                        "count": profile["count"],
                        "percentage": profile["percentage"],
                        "color": color,
                        "avg_income": round(avg_income, 2),
                        "avg_savings": round(avg_savings, 2),
                        "avg_spending": round(avg_spending, 2),
                        "recommendations": self._get_recommendations(profile),
                    }
                )
            async with self:
                self.kpis = kpis
                self.segment_distribution = dist_data
                self.segment_insights = insights_data
                self.insights_generated = True
                self.is_generating = False
        except Exception as e:
            logging.exception(f"Insight generation failed: {e}")
            async with self:
                self.is_generating = False
            yield rx.toast.error(f"Insight generation failed: {str(e)}")