from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_default_docker_compose_includes_vps_update_mounts():
    compose = (PROJECT_ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert "- ./:/app/source" in compose
    assert "- /var/run/docker.sock:/var/run/docker.sock" in compose
    assert "updater:" in compose
    assert "profiles:" in compose
    assert "- update" in compose


def test_docker_env_example_enables_vps_update_by_default():
    env_example = (PROJECT_ROOT / ".env.docker.example").read_text(encoding="utf-8")

    assert "VPS_UPDATE_ENABLED=true" in env_example
    assert "docker-compose.update.yml" not in env_example
