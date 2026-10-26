"""Create and populate the ChromaDB collection used for candidate profiles."""

import json
import os
from collections.abc import Mapping, Sequence
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection


COLLECTION_NAME = "cynaris_intern_profiles"
DEFAULT_PERSIST_DIRECTORY = os.path.join(
    os.path.dirname(__file__),
    "chroma_data",
)


def create_collection(
    persist_directory: str = DEFAULT_PERSIST_DIRECTORY,
) -> Collection:
    """Create the persistent client and return the candidate profile collection."""
    client = chromadb.PersistentClient(path=persist_directory)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "description": "Vector embeddings and metadata for CIA career profiles",
            "hnsw:space": "cosine",
        },
    )


def build_profile_metadata(
    candidate_id: str,
    skills: Sequence[str],
    scores: Mapping[str, int | float],
    history: Sequence[Mapping[str, Any]],
) -> dict[str, str]:
    """Convert profile metadata to Chroma-compatible scalar values."""
    if not candidate_id.strip():
        raise ValueError("candidate_id must be a non-empty string")
    if not all(isinstance(skill, str) for skill in skills):
        raise TypeError("skills must contain only strings")

    return {
        "candidate_id": candidate_id,
        "skills": json.dumps(list(skills)),
        "scores": json.dumps(dict(scores)),
        "history": json.dumps(list(history)),
    }


if __name__ == "__main__":
    collection = create_collection()
    print(
        f"Ready: {COLLECTION_NAME} "
        f"({collection.count()} profiles currently indexed)"
    )
