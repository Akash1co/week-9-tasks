"""Tests for the ChromaDB role seeding and vector search pipeline."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIRECTORY = Path(__file__).resolve().parents[1]
PROJECT_ROOT = SCRIPT_DIRECTORY.parent
sys.path.insert(0, str(SCRIPT_DIRECTORY))

from role_profiles import ROLE_PROFILES  # noqa: E402
from vector_search_roles import search_roles  # noqa: E402


class VectorSearchRolesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.persist_directory = tempfile.TemporaryDirectory()
        self.environment = os.environ.copy()
        self.environment["CIA_CHROMA_PERSIST_DIRECTORY"] = self.persist_directory.name

    def tearDown(self) -> None:
        self.persist_directory.cleanup()

    def test_seed_and_cli_search_return_five_distinct_ranked_roles(self) -> None:
        role_names = [profile["role"] for profile in ROLE_PROFILES]
        self.assertEqual(len(role_names), 20)
        self.assertEqual(len(set(role_names)), 20)
        self.assertTrue(all(profile["required_skills"] for profile in ROLE_PROFILES))
        self.assertTrue(all(profile["match_criteria"] for profile in ROLE_PROFILES))
        self.assertTrue(all(profile["metadata"] for profile in ROLE_PROFILES))

        for _ in range(2):
            seed_process = subprocess.run(
                [sys.executable, str(SCRIPT_DIRECTORY / "seed_chromadb_roles.py")],
                capture_output=True,
                check=True,
                cwd=PROJECT_ROOT,
                env=self.environment,
                text=True,
            )
            self.assertEqual(seed_process.stdout.strip(), "Seeded 20 role profiles.")

        process = subprocess.run(
            [sys.executable, str(SCRIPT_DIRECTORY / "vector_search_roles.py")],
            input=json.dumps({"skills": ["Python", "SQL", "Data Visualization"]}),
            capture_output=True,
            check=True,
            cwd=PROJECT_ROOT,
            env=self.environment,
            text=True,
        )
        result = json.loads(process.stdout)
        matches = result["matches"]

        self.assertEqual(len(matches), 5)
        self.assertEqual(len({match["role"] for match in matches}), 5)
        self.assertEqual(matches[0]["role"], "Data Analyst")
        for match in matches:
            self.assertGreaterEqual(match["match_percentage"], 0)
            self.assertLessEqual(match["match_percentage"], 100)
            self.assertTrue(match["required_skills"])
            self.assertIsInstance(match["missing_skills"], list)
            self.assertTrue(match["match_criteria"])
            self.assertTrue(match["metadata"])

    def test_search_rejects_empty_skill_profiles(self) -> None:
        with self.assertRaises(ValueError):
            search_roles([])


if __name__ == "__main__":
    unittest.main()
