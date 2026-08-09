"""Deterministic, auditable recommendations computed from current marts."""

from typing import Any

from app.services.api_database import fetch_one
from app.services.stats_service import t_test_review_late


async def build_recommendations() -> list[dict[str, Any]]:
    recommendations: list[dict[str, Any]] = []
    underperforming = await fetch_one(
        """WITH months AS (
             SELECT date_trunc('month',max(date)) latest FROM marts.revenue_by_region
           ), growth AS (
             SELECT state,
               sum(revenue) FILTER (WHERE date >= latest) current_revenue,
               sum(revenue) FILTER (WHERE date >= latest-interval '1 month'
                                    AND date < latest) prior_revenue
             FROM marts.revenue_by_region CROSS JOIN months
             WHERE date >= latest-interval '1 month' GROUP BY state
           )
           SELECT state,current_revenue,prior_revenue,
             round(100.0*(current_revenue-prior_revenue)/nullif(prior_revenue,0),2)
               mom_growth_pct
           FROM growth WHERE prior_revenue>0 ORDER BY mom_growth_pct LIMIT 1"""
    )
    if underperforming:
        recommendations.append(
            {
                "id": f"regional-growth-{underperforming['state']}",
                "category": "regional",
                "severity": "medium",
                "title": "Review the weakest regional growth",
                "description": (
                    f"Assess marketing allocation in {underperforming['state']}, "
                    "the lowest month-over-month growth region."
                ),
                "supporting_metric": underperforming,
            }
        )
    region = await fetch_one(
        """SELECT state, round(100.0*sum(late_count)/nullif(sum(delivered_count),0),2) late_rate
           FROM marts.delivery_performance GROUP BY state HAVING sum(delivered_count)>0
           ORDER BY late_rate DESC LIMIT 1"""
    )
    if region:
        recommendations.append(
            {
                "id": f"delivery-{region['state']}",
                "category": "delivery",
                "severity": "high",
                "title": "Prioritize the highest-delay region",
                "description": f"Review carrier capacity and dispatch controls in {region['state']}.",
                "supporting_metric": region,
            }
        )
    category = await fetch_one(
        """SELECT category,sum(revenue) revenue,sum(units)::integer units
           FROM marts.revenue_by_category GROUP BY category ORDER BY revenue DESC LIMIT 1"""
    )
    if category:
        recommendations.append(
            {
                "id": f"inventory-{category['category']}",
                "category": "inventory",
                "severity": "medium",
                "title": "Protect inventory for the leading category",
                "description": f"Maintain availability for {category['category']}, the highest-revenue category.",
                "supporting_metric": category,
            }
        )
    segment = await fetch_one(
        """SELECT segment,customer_count,avg_clv FROM marts.customer_segments
           ORDER BY avg_clv DESC LIMIT 1"""
    )
    if segment:
        recommendations.append(
            {
                "id": f"retention-{segment['segment']}",
                "category": "customer",
                "severity": "medium",
                "title": "Target the highest-value customer segment",
                "description": f"Build a retention campaign for the {segment['segment']} segment.",
                "supporting_metric": segment,
            }
        )
    satisfaction = await fetch_one(
        """SELECT state,
             sum(avg_review_score*review_count)/nullif(sum(review_count),0) avg_score
           FROM marts.review_summary WHERE state IS NOT NULL GROUP BY state
           ORDER BY avg_score LIMIT 1"""
    )
    late_test = await t_test_review_late()
    if satisfaction and (late_test.get("p_value") or 1) < 0.05:
        recommendations.append(
            {
                "id": f"satisfaction-{satisfaction['state']}",
                "category": "satisfaction",
                "severity": "high",
                "title": "Improve satisfaction in the lowest-score region",
                "description": (
                    f"Prioritize delivery experience in {satisfaction['state']}; "
                    "the Phase 3 late-delivery review-score test is significant."
                ),
                "supporting_metric": {
                    **satisfaction,
                    "late_delivery_ttest_p_value": late_test["p_value"],
                },
            }
        )
    return recommendations
