"""Shared ChromaDB configuration and internship role profiles."""

import json
import os
from pathlib import Path
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection


COLLECTION_NAME = "cynaris_career_roles"
DEFAULT_PERSIST_DIRECTORY = Path(__file__).resolve().parents[1] / "storage" / "app" / "chromadb"

ROLE_PROFILES: list[dict[str, Any]] = [
    {
        "role": "Backend Software Engineer",
        "required_skills": ["Python", "Django", "REST APIs", "PostgreSQL", "Git"],
        "match_criteria": "Build and maintain reliable server-side applications, APIs, and data services.",
        "metadata": {"category": "Software Engineering", "experience_level": "Entry-level", "work_mode": "Hybrid"},
    },
    {
        "role": "Full Stack Developer",
        "required_skills": ["JavaScript", "React", "Node.js", "HTML/CSS", "REST APIs"],
        "match_criteria": "Deliver end-to-end web features across responsive user interfaces and backend services.",
        "metadata": {"category": "Software Engineering", "experience_level": "Entry-level", "work_mode": "Hybrid"},
    },
    {
        "role": "Frontend Developer",
        "required_skills": ["HTML/CSS", "JavaScript", "React", "TypeScript", "Accessibility"],
        "match_criteria": "Create accessible, responsive, and maintainable user interfaces for web products.",
        "metadata": {"category": "Software Engineering", "experience_level": "Entry-level", "work_mode": "Remote"},
    },
    {
        "role": "Data Analyst",
        "required_skills": ["SQL", "Excel", "Python", "Data Visualization", "Statistics"],
        "match_criteria": "Turn business data into reliable reports, dashboards, and actionable insights.",
        "metadata": {"category": "Data", "experience_level": "Entry-level", "work_mode": "Hybrid"},
    },
    {
        "role": "Data Scientist",
        "required_skills": ["Python", "Statistics", "Machine Learning", "Pandas", "SQL"],
        "match_criteria": "Apply statistical analysis and machine learning to answer product and business questions.",
        "metadata": {"category": "Data", "experience_level": "Entry-level", "work_mode": "Hybrid"},
    },
    {
        "role": "Machine Learning Engineer",
        "required_skills": ["Python", "Machine Learning", "TensorFlow", "APIs", "Docker"],
        "match_criteria": "Build, evaluate, and deploy machine-learning models as production services.",
        "metadata": {"category": "AI and Data", "experience_level": "Entry-level", "work_mode": "Hybrid"},
    },
    {
        "role": "DevOps Engineer",
        "required_skills": ["Linux", "Docker", "Kubernetes", "CI/CD", "AWS"],
        "match_criteria": "Automate software delivery and operate scalable, dependable cloud infrastructure.",
        "metadata": {"category": "Cloud and Infrastructure", "experience_level": "Entry-level", "work_mode": "Hybrid"},
    },
    {
        "role": "Cloud Engineer",
        "required_skills": ["AWS", "Terraform", "Linux", "Networking", "Docker"],
        "match_criteria": "Provision and support secure cloud environments using infrastructure as code.",
        "metadata": {"category": "Cloud and Infrastructure", "experience_level": "Entry-level", "work_mode": "Remote"},
    },
    {
        "role": "Cybersecurity Analyst",
        "required_skills": ["Network Security", "SIEM", "Incident Response", "Linux", "Python"],
        "match_criteria": "Monitor systems, investigate security alerts, and support defensive incident response.",
        "metadata": {"category": "Security", "experience_level": "Entry-level", "work_mode": "On-site"},
    },
    {
        "role": "QA Automation Engineer",
        "required_skills": ["Selenium", "Python", "Software Testing", "API Testing", "CI/CD"],
        "match_criteria": "Design automated tests that improve application quality and prevent regressions.",
        "metadata": {"category": "Quality Engineering", "experience_level": "Entry-level", "work_mode": "Hybrid"},
    },
    {
        "role": "Mobile App Developer",
        "required_skills": ["Kotlin", "Android", "REST APIs", "Git", "Software Testing"],
        "match_criteria": "Develop and test Android applications that integrate with backend services.",
        "metadata": {"category": "Mobile Development", "experience_level": "Entry-level", "work_mode": "Hybrid"},
    },
    {
        "role": "iOS Developer",
        "required_skills": ["Swift", "SwiftUI", "XCTest", "REST APIs", "Git"],
        "match_criteria": "Build polished iOS applications and validate them with automated tests.",
        "metadata": {"category": "Mobile Development", "experience_level": "Entry-level", "work_mode": "Hybrid"},
    },
    {
        "role": "UI/UX Designer",
        "required_skills": ["Figma", "User Research", "Wireframing", "Prototyping", "Accessibility"],
        "match_criteria": "Research user needs and translate them into tested, accessible interface designs.",
        "metadata": {"category": "Design", "experience_level": "Entry-level", "work_mode": "Remote"},
    },
    {
        "role": "Product Manager",
        "required_skills": ["Product Strategy", "User Research", "Roadmap Planning", "Analytics", "Communication"],
        "match_criteria": "Coordinate product discovery and delivery using customer evidence and measurable outcomes.",
        "metadata": {"category": "Product", "experience_level": "Entry-level", "work_mode": "Hybrid"},
    },
    {
        "role": "Business Analyst",
        "required_skills": ["Requirements Gathering", "SQL", "Documentation", "Process Mapping", "Stakeholder Communication"],
        "match_criteria": "Document business needs and translate stakeholder workflows into clear requirements.",
        "metadata": {"category": "Business Analysis", "experience_level": "Entry-level", "work_mode": "Hybrid"},
    },
    {
        "role": "Technical Writer",
        "required_skills": ["Technical Writing", "API Documentation", "Markdown", "Git", "Editing"],
        "match_criteria": "Produce clear, accurate documentation for technical products and developer audiences.",
        "metadata": {"category": "Technical Communication", "experience_level": "Entry-level", "work_mode": "Remote"},
    },
    {
        "role": "Database Administrator",
        "required_skills": ["SQL", "PostgreSQL", "Database Backups", "Performance Tuning", "Linux"],
        "match_criteria": "Maintain database reliability, security, backups, and query performance.",
        "metadata": {"category": "Data and Infrastructure", "experience_level": "Entry-level", "work_mode": "Hybrid"},
    },
    {
        "role": "AI Engineer",
        "required_skills": ["Python", "Large Language Models", "Prompt Engineering", "APIs", "Vector Databases"],
        "match_criteria": "Integrate language models and retrieval systems into useful, evaluated applications.",
        "metadata": {"category": "AI and Data", "experience_level": "Entry-level", "work_mode": "Hybrid"},
    },
    {
        "role": "Network Engineer",
        "required_skills": ["TCP/IP", "Routing", "Switching", "Firewalls", "Network Monitoring"],
        "match_criteria": "Configure and troubleshoot secure enterprise network connectivity and services.",
        "metadata": {"category": "Networking", "experience_level": "Entry-level", "work_mode": "On-site"},
    },
    {
        "role": "Software Support Engineer",
        "required_skills": ["Troubleshooting", "Linux", "SQL", "Customer Communication", "Scripting"],
        "match_criteria": "Diagnose technical product issues and provide clear, effective customer support.",
        "metadata": {"category": "Technical Support", "experience_level": "Entry-level", "work_mode": "Hybrid"},
    },
]


def get_roles_collection() -> Collection:
    """Return the persistent role collection configured for cosine distance."""
    persist_directory = os.getenv(
        "CIA_CHROMA_PERSIST_DIRECTORY",
        str(DEFAULT_PERSIST_DIRECTORY),
    )
    client = chromadb.PersistentClient(path=persist_directory)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "description": "CIA internship and career role profiles",
            "hnsw:space": "cosine",
        },
    )


def role_document(profile: dict[str, Any]) -> str:
    """Build the searchable role description from its skills and criteria."""
    return (
        f"{profile['role']}. Required skills: "
        f"{', '.join(profile['required_skills'])}. "
        f"{profile['match_criteria']}"
    )


def role_metadata(profile: dict[str, Any]) -> dict[str, str]:
    """Convert a role profile into ChromaDB-compatible scalar metadata."""
    return {
        "role": profile["role"],
        "required_skills": json.dumps(profile["required_skills"]),
        "match_criteria": profile["match_criteria"],
        **profile["metadata"],
    }
