"""
Unit & Configuration Test Suite for Docker Packaging & Deployment (Phase 4, Step 4.2).
Validates:
1. Dockerfile structure, pinned base image, non-root user isolation, exposed port, and healthcheck.
2. .dockerignore rules ensuring zero credential, secret, or private data leakage into build context.
3. docs/docker_run.md documentation completeness and verification commands.
"""

import os
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_dockerfile_exists_and_pinned_base_image():
    """Validates that Dockerfile exists and pins a secure slim Python base image."""
    dockerfile_path = os.path.join(BASE_DIR, "Dockerfile")
    assert os.path.exists(dockerfile_path), "Dockerfile missing at repository root!"

    with open(dockerfile_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Base image pinned
    assert "FROM python:3.12" in content, "Dockerfile must pin Python 3.12 base image"
    assert "slim" in content, "Dockerfile should use lightweight slim variant"


def test_dockerfile_security_and_non_root_user():
    """Validates that Dockerfile implements non-root user execution policy."""
    dockerfile_path = os.path.join(BASE_DIR, "Dockerfile")
    with open(dockerfile_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Non-root user creation and declaration
    assert "useradd" in content, "Dockerfile must create dedicated non-root user"
    assert "USER appuser" in content, "Dockerfile must switch execution to non-root USER"

    # Working dir and port
    assert "WORKDIR /app" in content, "Dockerfile must specify WORKDIR /app"
    assert "EXPOSE 8000" in content, "Dockerfile must expose port 8000"

    # Healthcheck directive
    assert "HEALTHCHECK" in content, "Dockerfile must define automated container HEALTHCHECK"

    # Production Uvicorn command
    assert "uvicorn" in content, "Dockerfile CMD must execute uvicorn serving engine"


def test_dockerignore_rules_and_secret_exclusion():
    """Verifies that .dockerignore excludes credentials, private data, checkpoints, and caches."""
    dockerignore_path = os.path.join(BASE_DIR, ".dockerignore")
    assert os.path.exists(dockerignore_path), ".dockerignore missing at repository root!"

    with open(dockerignore_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith("#")]

    required_patterns = [
        "data/private/",
        ".env",
        ".git/",
        ".venv/",
        "checkpoints/*.pt",
        "__pycache__/"
    ]

    for pat in required_patterns:
        matched = any(pat in line for line in lines)
        assert matched, f".dockerignore must exclude '{pat}' to protect secrets and optimize build size"


def test_docker_run_documentation_deliverable():
    """Validates that docs/docker_run.md exists and contains complete operational instructions."""
    doc_path = os.path.join(BASE_DIR, "docs", "docker_run.md")
    assert os.path.exists(doc_path), "docs/docker_run.md missing!"

    with open(doc_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Key instructions
    assert "docker build" in content
    assert "docker run" in content
    assert "hanguynthun/hanoi-temperature:v1.0.0" in content
    assert "appuser" in content
    assert "curl" in content
    assert "/health" in content
    assert "/predict" in content
    assert "docker push" in content

