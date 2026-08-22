"""Deterministic recommendations backed only by migrated Indian-data marts."""

from typing import Any

from app.services.api_database import fetch_one


async def build_recommendations() -> list[dict[str, Any]]:
    """Build auditable business actions without using retired Olist concepts."""
    recommendations: list[dict[str, Any]] = []

    region = await fetch_one(
        """WITH months AS (
             SELECT date_trunc('month',max(date)) latest
             FROM marts.revenue_by_region
           ), growth AS (
             SELECT region,
               sum(revenue) FILTER (WHERE date >= latest) current_revenue,
               sum(revenue) FILTER (
                 WHERE date >= latest-interval '1 month' AND date < latest
               ) prior_revenue
             FROM marts.revenue_by_region CROSS JOIN months
             WHERE date >= latest-interval '1 month' GROUP BY region
           )
           SELECT region,current_revenue,prior_revenue,
             round(100.0*(current_revenue-prior_revenue)/nullif(prior_revenue,0),2)
               mom_growth_pct
           FROM growth WHERE prior_revenue>0 ORDER BY mom_growth_pct LIMIT 1"""
    )
    if region:
        recommendations.append(
            {
                "id": f"regional-growth-{region['region'].lower()}",
                "category": "regional",
                "severity": "medium",
                "title": "Review the weakest regional growth",
                "description": (
                    f"Assess the revenue trend in the trusted {region['region']} "
                    "region, which has the lowest latest-month growth."
                ),
                "supporting_metric": region,
            }
        )

    discount = await fetch_one(
        """SELECT discount_band,sum(order_count)::integer order_count,
                  sum(revenue) revenue,sum(total_profit) total_profit,
                  100.0*sum(total_profit)/nullif(sum(revenue),0) profit_margin_pct
           FROM marts.category_discount_profit GROUP BY discount_band
           ORDER BY profit_margin_pct LIMIT 1"""
    )
    if discount:
        recommendations.append(
            {
                "id": f"margin-{discount['discount_band']}",
                "category": "profitability",
                "severity": "high",
                "title": "Protect margin in the weakest discount band",
                "description": (
                    f"Review pricing controls for the {discount['discount_band']} "
                    "discount band, which has the lowest observed profit margin."
                ),
                "supporting_metric": discount,
            }
        )

    category = await fetch_one(
        """SELECT category,sum(revenue) revenue,sum(total_profit) total_profit,
                  sum(order_count)::integer order_count,
                  100.0*sum(total_profit)/nullif(sum(revenue),0) profit_margin_pct
           FROM marts.revenue_by_category GROUP BY category
           ORDER BY total_profit DESC LIMIT 1"""
    )
    if category:
        recommendations.append(
            {
                "id": f"category-profit-{category['category']}",
                "category": "category",
                "severity": "medium",
                "title": "Protect the leading profit category",
                "description": (
                    f"Maintain availability for {category['category']}, the category "
                    "contributing the most total profit."
                ),
                "supporting_metric": category,
            }
        )

    segment = await fetch_one(
        """SELECT segment,order_value_tier,sum(customer_count)::integer customer_count,
                  sum(avg_order_value*customer_count)/nullif(sum(customer_count),0)
                    avg_order_value,
                  sum(avg_profit*customer_count)/nullif(sum(customer_count),0) avg_profit
           FROM marts.customer_segments GROUP BY segment,order_value_tier
           ORDER BY avg_profit DESC LIMIT 1"""
    )
    if segment:
        recommendations.append(
            {
                "id": f"segment-{segment['segment']}-{segment['order_value_tier']}",
                "category": "customer",
                "severity": "medium",
                "title": "Prioritize the strongest cross-sectional segment",
                "description": (
                    f"Focus relevant offers on {segment['segment']} customers in the "
                    f"{segment['order_value_tier']} order-value tier."
                ),
                "supporting_metric": segment,
            }
        )

    return recommendations
