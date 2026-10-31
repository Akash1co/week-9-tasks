import os
import unittest
from unittest.mock import Mock, patch

from pydantic import ValidationError

from scripts.langgraph_learning_path import (
    Assessment,
    GapAnalysis,
    LearningPathRequest,
    PathSummary,
    PlanReview,
    StudyPlan,
    _fallback_for_node,
    generate_learning_path,
)


class LearningPathTests(unittest.TestCase):
    def test_fallback_graph_returns_eight_weeks_and_56_daily_topics(self) -> None:
        request = LearningPathRequest(
            target_role="Full Stack Developer",
            skills=["PHP", "HTML"],
            skill_gaps=["Laravel", "API design"],
            weekly_hours=7,
        )
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
            result = generate_learning_path(request)

        self.assertEqual(len(result["schedule"]), 8)
        self.assertTrue(all(len(week["days"]) == 7 for week in result["schedule"]))
        self.assertEqual(
            [topic["day"] for week in result["schedule"] for topic in week["days"]],
            list(range(1, 8)) * 8,
        )
        self.assertIn("gantt", result["mermaid"])
        self.assertEqual(len(result["fallback_nodes"]), 5)

    def test_configured_groq_path_makes_one_call_for_each_graph_node(self) -> None:
        request = LearningPathRequest(
            target_role="Full Stack Developer",
            skills=["PHP"],
            skill_gaps=["Laravel"],
        )
        request_state = {"request": request.model_dump(mode="json")}
        responses = {
            Assessment: Assessment(
                current_strengths=["PHP"],
                focus_areas=["Laravel"],
                role_outcomes=["Build full-stack applications"],
            ),
            GapAnalysis: GapAnalysis(
                skill_gaps=["Laravel"],
                priority_skills=["Laravel"],
            ),
            StudyPlan: _fallback_for_node(
                "BuildPlan",
                {
                    **request_state,
                    "gap_analysis": {"priority_skills": ["Laravel"]},
                },
            ),
            PlanReview: PlanReview(approved=True),
            PathSummary: PathSummary(
                title="Full Stack Developer learning path",
                summary="Build full-stack skills through daily practice.",
                outcomes=["Deliver a tested full-stack capstone"],
            ),
        }
        chat_groq = Mock()
        chat_groq.return_value.with_structured_output.side_effect = (
            lambda schema: Mock(invoke=Mock(return_value=responses[schema]))
        )

        with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}), patch(
            "scripts.langgraph_learning_path.ChatGroq", chat_groq
        ):
            result = generate_learning_path(request)

        self.assertEqual(chat_groq.call_count, 5)
        self.assertEqual(chat_groq.return_value.with_structured_output.call_count, 5)
        self.assertEqual(result["fallback_nodes"], [])

    def test_plan_rejects_missing_days(self) -> None:
        with self.assertRaises(ValidationError):
            StudyPlan.model_validate({"weeks": []})


if __name__ == "__main__":
    unittest.main()
