from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_dockerfile_keeps_vps_updater_build_requirements():
    dockerfile = (PROJECT_ROOT / "Dockerfile").read_text(encoding="utf-8")

    app_stage = dockerfile.split("FROM ${DOCKER_IMAGE_PREFIX}library/python:3.11-slim AS app", 1)[1]

    assert "ARG DOCKER_COMPOSE_VERSION" in app_stage
    assert "docker-cli" in app_stage
    assert "docker.io" not in app_stage
    assert "docker compose version" in app_stage
