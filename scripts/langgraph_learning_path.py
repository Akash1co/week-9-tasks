import json
import os
import sys
from datetime import date, timedelta
from typing import Any, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LearningPathRequest(StrictModel):
    target_role: str = Field(min_length=1, max_length=120)
    skills: list[str] = Field(default_factory=list, max_length=50)
    skill_gaps: list[str] = Field(default_factory=list, max_length=50)
    experience_level: str = Field(default="intermediate", max_length=80)
    weekly_hours: int = Field(default=7, ge=1, le=40)
    profile: dict[str, Any] = Field(default_factory=dict)


class Assessment(StrictModel):
    current_strengths: list[str] = Field(min_length=1, max_length=12)
    focus_areas: list[str] = Field(min_length=1, max_length=12)
    role_outcomes: list[str] = Field(min_length=1, max_length=8)


class GapAnalysis(StrictModel):
    skill_gaps: list[str] = Field(min_length=1, max_length=12)
    priority_skills: list[str] = Field(min_length=1, max_length=8)
    prerequisites: list[str] = Field(default_factory=list, max_length=12)


class DailyTopic(StrictModel):
    day: int = Field(ge=1, le=7)
    topic: str = Field(min_length=3, max_length=160)
    practice: str = Field(min_length=3, max_length=240)
    estimated_hours: float = Field(gt=0, le=12)


class WeekPlan(StrictModel):
    week: int = Field(ge=1, le=8)
    theme: str = Field(min_length=3, max_length=120)
    days: list[DailyTopic] = Field(min_length=7, max_length=7)


class StudyPlan(StrictModel):
    weeks: list[WeekPlan] = Field(min_length=8, max_length=8)

    @model_validator(mode="after")
    def require_consecutive_weeks_and_days(self) -> "StudyPlan":
        if [week.week for week in self.weeks] != list(range(1, 9)):
            raise ValueError("The study plan must contain weeks 1 through 8 in order.")
        if any([topic.day for topic in week.days] != list(range(1, 8)) for week in self.weeks):
            raise ValueError("Each week must contain days 1 through 7 in order.")
        return self


class PlanReview(StrictModel):
    approved: bool
    comments: list[str] = Field(default_factory=list, max_length=12)


class PathSummary(StrictModel):
    title: str = Field(min_length=3, max_length=120)
    summary: str = Field(min_length=10, max_length=600)
    outcomes: list[str] = Field(min_length=1, max_length=8)


class LearningPathState(TypedDict, total=False):
    request: dict[str, Any]
    assessment: dict[str, Any]
    gap_analysis: dict[str, Any]
    study_plan: dict[str, Any]
    plan_review: dict[str, Any]
    summary: dict[str, Any]
    fallback_nodes: list[str]
    result: dict[str, Any]


WEEK_THEMES = [
    "Role foundations and skill baseline",
    "Core language and problem solving",
    "Framework and platform fundamentals",
    "Data modeling and API development",
    "Testing, debugging, and code quality",
    "Architecture, integration, and security",
    "Deployment, observability, and operations",
    "Capstone delivery and interview preparation",
]


def _fallback_for_node(node: str, state: LearningPathState) -> BaseModel:
    request = state["request"]
    skills = request.get("skills", [])
    gaps = request.get("skill_gaps", [])
    if node == "AssessState":
        return Assessment(
            current_strengths=skills or ["Foundational software development"],
            focus_areas=gaps or [f"Role-specific skills for {request['target_role']}"],
            role_outcomes=[
                f"Design, build, test, and explain work relevant to {request['target_role']}"
            ],
        )
    if node == "IdentifyGaps":
        focus_areas = state.get("assessment", {}).get("focus_areas", [])
        priorities = list(dict.fromkeys(gaps + focus_areas))[:8]
        return GapAnalysis(
            skill_gaps=priorities or [f"Core competencies for {request['target_role']}"],
            priority_skills=priorities or [f"Core competencies for {request['target_role']}"],
        )
    if node == "BuildPlan":
        priority_skills = state.get("gap_analysis", {}).get("priority_skills", [])
        weeks = []
        for week_number, theme in enumerate(WEEK_THEMES, start=1):
            focus = priority_skills[(week_number - 1) % len(priority_skills)]
            days = [
                DailyTopic(
                    day=day,
                    topic=f"{theme}: {focus} - day {day}",
                    practice=(
                        f"Complete a focused {focus} exercise and record one "
                        "takeaway or working artifact."
                    ),
                    estimated_hours=round(request.get("weekly_hours", 7) / 7, 3),
                )
                for day in range(1, 8)
            ]
            weeks.append(WeekPlan(week=week_number, theme=theme, days=days))
        return StudyPlan(weeks=weeks)
    if node == "ValidatePlan":
        return PlanReview(
            approved=True,
            comments=["Schedule shape and all 56 daily topics passed validation."],
        )
    return PathSummary(
        title=f"8-week learning path for {request['target_role']}",
        summary=(
            "A paced, day-by-day plan that moves from role foundations to a "
            "portfolio-ready capstone and interview preparation."
        ),
        outcomes=state.get("assessment", {}).get(
            "role_outcomes", [f"Build readiness for {request['target_role']}"]
        ),
    )


def _call_node_model(
    node: str,
    state: LearningPathState,
    schema: type[BaseModel],
    instructions: str,
) -> tuple[BaseModel, bool]:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        print(f"{node}: GROQ_API_KEY is not configured; using deterministic fallback.", file=sys.stderr)
        return _fallback_for_node(node, state), True

    try:
        model = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            api_key=api_key,
            temperature=0.2,
            timeout=45,
            max_retries=0,
        )
        response = model.with_structured_output(schema).invoke(
            [
                SystemMessage(content=instructions),
                HumanMessage(content=json.dumps(state, ensure_ascii=False)),
            ]
        )
        return (response if isinstance(response, schema) else schema.model_validate(response)), False
    except Exception as exc:
        print(
            f"{node}: Groq request or structured response failed "
            f"({type(exc).__name__}); using deterministic fallback.",
            file=sys.stderr,
        )
        return _fallback_for_node(node, state), True


def assess_state(state: LearningPathState) -> dict[str, Any]:
    assessment, used_fallback = _call_node_model(
        "AssessState",
        state,
        Assessment,
        "Assess the candidate's supplied skills and profile for the target role. "
        "Return grounded strengths, focus areas, and measurable role outcomes. "
        "Do not invent qualifications.",
    )
    return {
        "assessment": assessment.model_dump(mode="json"),
        "fallback_nodes": state.get("fallback_nodes", []) + (["AssessState"] if used_fallback else []),
    }


def identify_gaps(state: LearningPathState) -> dict[str, Any]:
    analysis, used_fallback = _call_node_model(
        "IdentifyGaps",
        state,
        GapAnalysis,
        "Identify and prioritize actionable skill gaps for the target role using "
        "the candidate request and assessment. Return concise skill names and "
        "prerequisites. Do not invent candidate experience.",
    )
    return {
        "gap_analysis": analysis.model_dump(mode="json"),
        "fallback_nodes": state.get("fallback_nodes", []) + (["IdentifyGaps"] if used_fallback else []),
    }


def build_plan(state: LearningPathState) -> dict[str, Any]:
    plan, used_fallback = _call_node_model(
        "BuildPlan",
        state,
        StudyPlan,
        "Build an exactly 8-week study schedule for the target role. Every week "
        "must contain exactly 7 ordered days, each with a specific topic, a "
        "hands-on practice task, and estimated hours. Make progression "
        "cumulative, use the candidate's weekly study hours, and finish with a "
        "capstone and interview practice. Return all 56 days.",
    )
    try:
        validated_plan = _validate_study_plan(
            StudyPlan.model_validate(plan.model_dump()),
            state["request"]["weekly_hours"],
        )
    except Exception as exc:
        print(
            f"BuildPlan: generated schedule failed validation ({type(exc).__name__}); "
            "using deterministic fallback.",
            file=sys.stderr,
        )
        validated_plan = _validate_study_plan(
            StudyPlan.model_validate(_fallback_for_node("BuildPlan", state).model_dump()),
            state["request"]["weekly_hours"],
        )
        used_fallback = True
    return {
        "study_plan": validated_plan.model_dump(mode="json"),
        "fallback_nodes": state.get("fallback_nodes", []) + (["BuildPlan"] if used_fallback else []),
    }


def validate_plan(state: LearningPathState) -> dict[str, Any]:
    _validate_study_plan(
        StudyPlan.model_validate(state["study_plan"]),
        state["request"]["weekly_hours"],
    )
    review, used_fallback = _call_node_model(
        "ValidatePlan",
        state,
        PlanReview,
        "Review the proposed schedule for a realistic 8-week progression, "
        "specific daily topics and practice, and coverage of the priority gaps. "
        "The schedule already passed structural validation. Return approval "
        "and concise comments; do not rewrite it.",
    )
    return {
        "plan_review": review.model_dump(mode="json"),
        "fallback_nodes": state.get("fallback_nodes", []) + (["ValidatePlan"] if used_fallback else []),
    }


def _validate_study_plan(plan: StudyPlan, weekly_hours: int) -> StudyPlan:
    if any(
        sum(topic.estimated_hours for topic in week.days) > weekly_hours + 0.01
        for week in plan.weeks
    ):
        raise ValueError("A week's daily study hours exceed the candidate's available time.")
    return plan


def _mermaid_gantt(weeks: list[WeekPlan]) -> str:
    start = date.today()
    lines = [
        "gantt",
        "    title 8-week learning path",
        "    dateFormat YYYY-MM-DD",
        "    axisFormat %b %d",
    ]
    for week in weeks:
        week_start = start + timedelta(days=(week.week - 1) * 7)
        lines.extend(
            [
                f"    section Week {week.week}",
                f"    Week {week.week}:w{week.week}, {week_start.isoformat()}, 7d",
            ]
        )
    return "\n".join(lines)


def output_plan(state: LearningPathState) -> dict[str, Any]:
    summary, used_fallback = _call_node_model(
        "OutputPlan",
        state,
        PathSummary,
        "Prepare a concise title, user-facing summary, and measurable outcomes "
        "for the candidate's validated learning path. Do not alter the schedule.",
    )
    plan = StudyPlan.model_validate(state["study_plan"])
    result = {
        **summary.model_dump(mode="json"),
        "schedule": plan.model_dump(mode="json")["weeks"],
        "mermaid": _mermaid_gantt(plan.weeks),
        "validation": state["plan_review"],
        "fallback_nodes": state.get("fallback_nodes", []) + (["OutputPlan"] if used_fallback else []),
    }
    return {"result": result}


def build_graph():
    graph = StateGraph(LearningPathState)
    graph.add_node("AssessState", assess_state)
    graph.add_node("IdentifyGaps", identify_gaps)
    graph.add_node("BuildPlan", build_plan)
    graph.add_node("ValidatePlan", validate_plan)
    graph.add_node("OutputPlan", output_plan)
    graph.add_edge(START, "AssessState")
    graph.add_edge("AssessState", "IdentifyGaps")
    graph.add_edge("IdentifyGaps", "BuildPlan")
    graph.add_edge("BuildPlan", "ValidatePlan")
    graph.add_edge("ValidatePlan", "OutputPlan")
    graph.add_edge("OutputPlan", END)
    return graph.compile()


def generate_learning_path(request: LearningPathRequest) -> dict[str, Any]:
    state = build_graph().invoke(
        {
            "request": request.model_dump(mode="json"),
            "fallback_nodes": [],
        }
    )
    return state["result"]


def main() -> int:
    try:
        raw_request = json.load(sys.stdin)
        if not isinstance(raw_request, dict):
            raise ValueError("Input must be a JSON object.")
        request = LearningPathRequest.model_validate(raw_request)
        result = generate_learning_path(request)
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"Learning path request failed: {exc}", file=sys.stderr)
        return 2
    sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
