"""Search ChromaDB for the five roles closest to a candidate skill profile."""

import json
import math
import sys
from typing import Any

from role_profiles import get_roles_collection


def _normalized_skill(skill: str) -> str:
    return " ".join(skill.casefold().split())


def search_roles(skills: list[str]) -> dict[str, list[dict[str, Any]]]:
    """Return the top five cosine-ranked roles and their candidate skill gaps."""
    normalized_skills = [_normalized_skill(skill) for skill in skills]
    if not normalized_skills or any(not skill for skill in normalized_skills):
        raise ValueError("skills must contain at least one non-empty string.")

    collection = get_roles_collection()
    role_count = collection.count()
    if role_count != 20:
        raise RuntimeError(
            "The role collection must contain exactly 20 profiles; "
            "run seed_chromadb_roles.py first."
        )

    query = "Candidate skills: " + ", ".join(skills)
    results = collection.query(
        query_texts=[query],
        n_results=min(5, role_count),
        include=["metadatas", "distances"],
    )
    ids = results["ids"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    matches: list[dict[str, Any]] = []

    for role_id, metadata, distance in zip(ids, metadatas, distances, strict=True):
        required_skills = json.loads(metadata["required_skills"])
        distance_value = float(distance)
        if not math.isfinite(distance_value):
            raise RuntimeError("ChromaDB returned a non-finite cosine distance.")
        cosine_similarity = max(0.0, min(1.0, 1.0 - distance_value))
        candidate_skills = set(normalized_skills)
        missing_skills = [
            skill
            for skill in required_skills
            if _normalized_skill(skill) not in candidate_skills
        ]
        matches.append(
            {
                "role_id": role_id,
                "role": metadata["role"],
                "match_percentage": round(cosine_similarity * 100, 1),
                "cosine_similarity": round(cosine_similarity, 4),
                "required_skills": required_skills,
                "missing_skills": missing_skills,
                "match_criteria": metadata["match_criteria"],
                "metadata": {
                    key: value
                    for key, value in metadata.items()
                    if key not in {"role", "required_skills", "match_criteria"}
                },
            }
        )

    if len(matches) != 5:
        raise RuntimeError(f"Expected five ranked role results, found {len(matches)}.")
    return {"matches": matches}


def main() -> int:
    payload = json.load(sys.stdin)
    if not isinstance(payload, dict):
        raise ValueError("Input must be a JSON object.")
    skills = payload.get("skills")
    if (
        not isinstance(skills, list)
        or not skills
        or any(not isinstance(skill, str) or not skill.strip() for skill in skills)
    ):
        raise ValueError("skills must be a non-empty array of non-empty strings.")

    response = search_roles([skill.strip() for skill in skills])
    sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
