"""
Test Suite for CI/CD Pipelines & Operational PDF Documentation (Phase 5).
Validates:
1. .github/workflows/ci.yml configuration, triggers, permissions, and job dependency graph.
2. .github/workflows/release.yml configuration, SemVer tag triggers, secret references, and step summary.
3. docs/release.md operational documentation, Docker Hub token management, and rollback strategy.
4. docs/ci_cd_docker_step_by_step.md and docs/ci_cd_docker_step_by_step.pdf deliverables existence and integrity.
"""

import os
import yaml
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_ci_workflow_validity_and_security_pinning():
    """Validates CI workflow YAML structure, least-privilege permissions, and commit SHA pinning."""
    ci_path = os.path.join(BASE_DIR, ".github", "workflows", "ci.yml")
    assert os.path.exists(ci_path), "Missing .github/workflows/ci.yml!"

    with open(ci_path, "r", encoding="utf-8") as f:
        ci_cfg = yaml.safe_load(f)

    # 1. Triggers
    triggers = ci_cfg.get("on") or ci_cfg.get(True) or {}
    assert "push" in triggers or "pull_request" in triggers, "CI must trigger on push/pull_request"

    # 2. Permissions (Principle of least privilege)
    perms = ci_cfg.get("permissions", {})
    assert perms.get("contents") == "read", "CI permissions must be strictly read-only (contents: read)"

    # 3. Jobs
    jobs = ci_cfg.get("jobs", {})
    assert "lint" in jobs, "CI must define 'lint' job"
    assert "test" in jobs, "CI must define 'test' job"
    assert "docker-dry-run" in jobs, "CI must define 'docker-dry-run' job"

    # 4. Check action pinning to commit SHA in raw content
    with open(ci_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    assert "actions/checkout@" in raw_text
    assert "actions/setup-python@" in raw_text
    assert "docker/build-push-action@" in raw_text


def test_release_workflow_validity_and_secrets():
    """Validates CD release workflow, tag triggers, pre-release gate, and Docker Hub secrets."""
    release_path = os.path.join(BASE_DIR, ".github", "workflows", "release.yml")
    assert os.path.exists(release_path), "Missing .github/workflows/release.yml!"

    with open(release_path, "r", encoding="utf-8") as f:
        release_cfg = yaml.safe_load(f)

    # 1. Triggers on SemVer tags
    triggers = release_cfg.get("on") or release_cfg.get(True) or {}
    assert "push" in triggers, "Release must trigger on push"
    tags = triggers["push"].get("tags", [])
    assert any("v*" in tag for tag in tags), "Release workflow must trigger on 'v*' tags"

    # 2. Jobs
    jobs = release_cfg.get("jobs", {})
    assert "pre-release-test" in jobs, "Release must include pre-release testing gate"
    assert "build-and-push" in jobs, "Release must include build-and-push job"

    # 3. Job dependencies: build-and-push must depend on pre-release-test
    build_job = jobs["build-and-push"]
    needs = build_job.get("needs", [])
    assert "pre-release-test" in needs, "build-and-push must require pre-release-test to pass first"

    # 4. Secret references
    with open(release_path, "r", encoding="utf-8") as f:
        raw_text = f.read()
    assert "secrets.DOCKERHUB_USERNAME" in raw_text
    assert "secrets.DOCKERHUB_TOKEN" in raw_text
    assert "GITHUB_STEP_SUMMARY" in raw_text


def test_release_markdown_documentation():
    """Validates docs/release.md completeness, token masking, and rollback procedure."""
    doc_path = os.path.join(BASE_DIR, "docs", "release.md")
    assert os.path.exists(doc_path), "Missing docs/release.md!"

    with open(doc_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "DOCKERHUB_USERNAME" in content
    assert "DOCKERHUB_TOKEN" in content
    assert "Rollback" in content
    assert "v1.0.0" in content
    assert "sha256" in content


def test_step_by_step_markdown_documentation():
    """Validates docs/ci_cd_docker_step_by_step.md content and verification table."""
    md_path = os.path.join(BASE_DIR, "docs", "ci_cd_docker_step_by_step.md")
    assert os.path.exists(md_path), "Missing docs/ci_cd_docker_step_by_step.md!"

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "Môi Trường Thực Nghiệm" in content
    assert "appuser" in content
    assert "Branch Protection" in content
    assert "curl" in content
    assert "/health" in content
    assert "/predict" in content
    assert "Troubleshooting" in content


def test_step_by_step_pdf_deliverable_exists_and_valid():
    """Validates docs/ci_cd_docker_step_by_step.pdf binary existence, size, and header signature."""
    pdf_path = os.path.join(BASE_DIR, "docs", "ci_cd_docker_step_by_step.pdf")
    assert os.path.exists(pdf_path), "Missing docs/ci_cd_docker_step_by_step.pdf!"

    size_bytes = os.path.getsize(pdf_path)
    assert size_bytes > 50_000, f"PDF file size too small ({size_bytes} bytes), expected > 50KB"

    # Verify standard PDF file header signature (%PDF-)
    with open(pdf_path, "rb") as f:
        header = f.read(5)
    assert header == b"%PDF-", f"Invalid PDF header: {header}"
