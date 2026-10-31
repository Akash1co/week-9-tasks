"""Seed the persistent ChromaDB collection with exactly 20 role profiles."""

from role_profiles import (
    ROLE_PROFILES,
    get_roles_collection,
    role_document,
    role_metadata,
)


def seed_roles() -> int:
    """Replace stale role records and leave exactly the configured profiles."""
    role_names = [profile["role"] for profile in ROLE_PROFILES]
    if len(role_names) != 20 or len(set(role_names)) != 20:
        raise ValueError("ROLE_PROFILES must contain exactly 20 distinct roles.")

    collection = get_roles_collection()
    role_ids = [f"role-{index:02d}" for index in range(1, len(ROLE_PROFILES) + 1)]
    existing_ids = collection.get()["ids"]
    stale_ids = [record_id for record_id in existing_ids if record_id not in role_ids]
    if stale_ids:
        collection.delete(ids=stale_ids)

    collection.upsert(
        ids=role_ids,
        documents=[role_document(profile) for profile in ROLE_PROFILES],
        metadatas=[role_metadata(profile) for profile in ROLE_PROFILES],
    )
    role_count = collection.count()
    if role_count != 20:
        raise RuntimeError(f"Expected 20 seeded roles, found {role_count}.")
    return role_count


if __name__ == "__main__":
    print(f"Seeded {seed_roles()} role profiles.")
