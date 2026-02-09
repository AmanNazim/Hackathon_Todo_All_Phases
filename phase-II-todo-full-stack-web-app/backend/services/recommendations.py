"""
Recommendations engine for generating personalized productivity suggestions.

Analyzes user task patterns and provides actionable recommendations to improve
productivity, task completion rates, and time management.
"""

from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from services.analytics import (
    calculate_completion_rate,
    calculate_adherence_rate,
    calculate_task_velocity,
    get_priority_distribution,
    get_overdue_count,
    calculate_task_totals
)


class RecommendationType:
    """Recommendation type constants."""
    COMPLETION = "completion"
    ADHERENCE = "adherence"
    VELOCITY = "velocity"
    PRIORITY = "priority"
    OVERDUE = "overdue"
    GENERAL = "general"


async def generate_recommendations(
    db: AsyncSession,
    user_id: UUID
) -> List[Dict[str, Any]]:
    """
    Generate personalized recommendations based on user analytics.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        List of recommendation dictionaries with type, message, and priority
    """
    recommendations = []

    # Get analytics data
    completion_rate = await calculate_completion_rate(db, user_id)
    adherence_data = await calculate_adherence_rate(db, user_id, 30)
    velocity = await calculate_task_velocity(db, user_id, 4)
    priority_dist = await get_priority_distribution(db, user_id)
    overdue_count = await get_overdue_count(db, user_id)
    totals = await calculate_task_totals(db, user_id)

    # Analyze completion rate
    if completion_rate < 30:
        recommendations.append({
            "type": RecommendationType.COMPLETION,
            "priority": "high",
            "message": "Your completion rate is low ({}%). Focus on completing existing tasks before creating new ones.".format(
                round(completion_rate, 1)
            ),
            "action": "Review your pending tasks and prioritize completing at least 3 tasks today."
        })
    elif completion_rate < 50:
        recommendations.append({
            "type": RecommendationType.COMPLETION,
            "priority": "medium",
            "message": "Your completion rate could be improved ({}%). Try breaking down large tasks into smaller, manageable pieces.".format(
                round(completion_rate, 1)
            ),
            "action": "Identify your largest pending task and split it into 3-5 smaller subtasks."
        })
    elif completion_rate >= 80:
        recommendations.append({
            "type": RecommendationType.COMPLETION,
            "priority": "low",
            "message": "Excellent completion rate ({}%)! Keep up the great work.".format(
                round(completion_rate, 1)
            ),
            "action": "Continue your current workflow and consider sharing your productivity tips with others."
        })

    # Analyze due date adherence
    adherence_rate = adherence_data["adherence_rate"]
    if adherence_rate < 50:
        recommendations.append({
            "type": RecommendationType.ADHERENCE,
            "priority": "high",
            "message": "You're frequently missing due dates ({}% on-time). Consider setting more realistic deadlines.".format(
                round(adherence_rate, 1)
            ),
            "action": "Review your upcoming due dates and extend any that seem too aggressive."
        })
    elif adherence_rate < 70:
        recommendations.append({
            "type": RecommendationType.ADHERENCE,
            "priority": "medium",
            "message": "Your due date adherence needs improvement ({}%). Try adding buffer time to your estimates.".format(
                round(adherence_rate, 1)
            ),
            "action": "When setting due dates, add 20-30% extra time to account for unexpected delays."
        })
    elif adherence_rate >= 90:
        recommendations.append({
            "type": RecommendationType.ADHERENCE,
            "priority": "low",
            "message": "Outstanding due date adherence ({}%)! Your time estimation skills are excellent.".format(
                round(adherence_rate, 1)
            ),
            "action": "Maintain your current planning approach."
        })

    # Analyze task velocity
    if velocity < 2:
        recommendations.append({
            "type": RecommendationType.VELOCITY,
            "priority": "high",
            "message": "Your task completion velocity is low ({} tasks/week). Focus on completing quick wins first.".format(
                round(velocity, 1)
            ),
            "action": "Identify 5 tasks that can be completed in under 30 minutes and tackle them this week."
        })
    elif velocity < 5:
        recommendations.append({
            "type": RecommendationType.VELOCITY,
            "priority": "medium",
            "message": "Your velocity could be improved ({} tasks/week). Consider time-blocking for focused work.".format(
                round(velocity, 1)
            ),
            "action": "Schedule 2-hour blocks of uninterrupted time for task completion."
        })
    elif velocity >= 10:
        recommendations.append({
            "type": RecommendationType.VELOCITY,
            "priority": "low",
            "message": "Impressive velocity ({} tasks/week)! You're highly productive.".format(
                round(velocity, 1)
            ),
            "action": "Consider mentoring others on your productivity techniques."
        })

    # Analyze priority distribution
    urgent_count = priority_dist.get("urgent", 0)
    high_count = priority_dist.get("high", 0)
    total_tasks = totals["total"]

    if total_tasks > 0:
        urgent_percentage = (urgent_count / total_tasks) * 100
        high_percentage = (high_count / total_tasks) * 100

        if urgent_percentage > 30:
            recommendations.append({
                "type": RecommendationType.PRIORITY,
                "priority": "high",
                "message": "Too many urgent tasks ({}%). This indicates poor planning or unrealistic expectations.".format(
                    round(urgent_percentage, 1)
                ),
                "action": "Review your urgent tasks and re-prioritize. Not everything can be urgent."
            })
        elif urgent_percentage + high_percentage > 60:
            recommendations.append({
                "type": RecommendationType.PRIORITY,
                "priority": "medium",
                "message": "High concentration of high-priority tasks ({}%). Consider better task prioritization.".format(
                    round(urgent_percentage + high_percentage, 1)
                ),
                "action": "Use the Eisenhower Matrix to categorize tasks by urgency and importance."
            })

    # Analyze overdue tasks
    if overdue_count > 10:
        recommendations.append({
            "type": RecommendationType.OVERDUE,
            "priority": "high",
            "message": "You have {} overdue tasks. This is creating unnecessary stress and reducing productivity.".format(
                overdue_count
            ),
            "action": "Dedicate time today to either complete, reschedule, or cancel these overdue tasks."
        })
    elif overdue_count > 5:
        recommendations.append({
            "type": RecommendationType.OVERDUE,
            "priority": "medium",
            "message": "You have {} overdue tasks. Address these to prevent them from piling up.".format(
                overdue_count
            ),
            "action": "Spend 30 minutes reviewing and updating your overdue tasks."
        })
    elif overdue_count == 0 and total_tasks > 10:
        recommendations.append({
            "type": RecommendationType.OVERDUE,
            "priority": "low",
            "message": "No overdue tasks! You're staying on top of your commitments.",
            "action": "Keep maintaining this excellent habit."
        })

    # General recommendations based on task count
    if totals["pending"] > 50:
        recommendations.append({
            "type": RecommendationType.GENERAL,
            "priority": "medium",
            "message": "You have {} pending tasks. This large backlog can be overwhelming.".format(
                totals["pending"]
            ),
            "action": "Consider archiving or deleting tasks that are no longer relevant."
        })
    elif totals["total"] < 5:
        recommendations.append({
            "type": RecommendationType.GENERAL,
            "priority": "low",
            "message": "You have very few tasks. Make sure you're capturing all your commitments.",
            "action": "Review your upcoming week and add any missing tasks or goals."
        })

    # Sort recommendations by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))

    return recommendations


async def get_top_recommendations(
    db: AsyncSession,
    user_id: UUID,
    limit: int = 3
) -> List[Dict[str, Any]]:
    """
    Get top N recommendations for a user.

    Args:
        db: Database session
        user_id: User ID
        limit: Maximum number of recommendations to return

    Returns:
        List of top recommendations
    """
    all_recommendations = await generate_recommendations(db, user_id)
    return all_recommendations[:limit]


async def get_recommendations_by_type(
    db: AsyncSession,
    user_id: UUID,
    recommendation_type: str
) -> List[Dict[str, Any]]:
    """
    Get recommendations filtered by type.

    Args:
        db: Database session
        user_id: User ID
        recommendation_type: Type of recommendations to retrieve

    Returns:
        List of recommendations of the specified type
    """
    all_recommendations = await generate_recommendations(db, user_id)
    return [
        rec for rec in all_recommendations
        if rec["type"] == recommendation_type
    ]


def format_recommendation_summary(recommendations: List[Dict[str, Any]]) -> str:
    """
    Format recommendations as a readable summary.

    Args:
        recommendations: List of recommendation dictionaries

    Returns:
        Formatted string summary
    """
    if not recommendations:
        return "No recommendations at this time. Keep up the good work!"

    summary_lines = ["Productivity Recommendations:\n"]

    for i, rec in enumerate(recommendations, 1):
        priority_emoji = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }.get(rec["priority"], "⚪")

        summary_lines.append(
            f"{i}. {priority_emoji} {rec['message']}\n"
            f"   Action: {rec['action']}\n"
        )

    return "\n".join(summary_lines)
