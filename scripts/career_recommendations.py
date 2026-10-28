import json
import os
import sys
from typing import Any

from crewai import Agent, Crew, LLM, Process, Task
from pydantic import BaseModel, Field


class Milestone(BaseModel):
    name: str
    action: str
    timeframe: str


class CareerPath(BaseModel):
    title: str
    overview: str
    required_competencies: list[str] = Field(min_length=1)
    milestones: list[Milestone] = Field(min_length=3)
    estimated_timeframe: str


class CareerRecommendations(BaseModel):
    career_paths: list[CareerPath] = Field(min_length=3, max_length=3)


def build_recommendations(candidate_data: dict[str, Any]) -> CareerRecommendations:
    agent = Agent(
        role="Senior Career Intelligence & Advisory Specialist",
        goal=(
            "Analyze candidate skill gaps and provide 3 tailored, actionable "
            "career advancement paths."
        ),
        backstory=(
            "Expert in technical recruitment, skill mapping, and software "
            "engineering career progression trajectories at top tech firms."
        ),
        llm=LLM(
            model=os.getenv("CREWAI_MODEL", "openai/gpt-4o-mini"),
            temperature=0.2,
        ),
        allow_delegation=False,
        verbose=False,
    )
    task = Task(
        description=(
            "Given this candidate profile, skill set, skill gaps, and target "
            "role, recommend exactly three distinct and realistic career paths. "
            "For every path include its title, a concise overview, required "
            "competencies, at least three ordered milestones with concrete "
            "actions and timeframes, and an overall estimated timeframe. "
            "Tailor the recommendations to the supplied data; do not invent "
            "qualifications. Candidate data: {candidate_data}"
        ),
        expected_output=(
            "A structured response containing exactly three distinct career "
            "paths, each with competencies, three or more milestones, and "
            "timeframes."
        ),
        agent=agent,
        output_json=CareerRecommendations,
    )
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=False,
    )
    output = crew.kickoff(
        inputs={"candidate_data": json.dumps(candidate_data, ensure_ascii=False)}
    )
    structured = output.pydantic

    if isinstance(structured, CareerRecommendations):
        return structured

    raw = output.raw
    return CareerRecommendations.model_validate_json(raw)


def main() -> int:
    candidate_data = json.load(sys.stdin)
    if not isinstance(candidate_data, dict):
        raise ValueError("Input must be a JSON object.")
    if not isinstance(candidate_data.get("target_role"), str):
        raise ValueError("target_role must be a string.")

    recommendations = build_recommendations(candidate_data)
    sys.stdout.write(
        json.dumps(recommendations.model_dump(), ensure_ascii=False) + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
