from pathlib import Path

import app.config as config_module


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
WORD_FORMATTER_ROOT = PACKAGE_ROOT / "backend" / "app" / "word_formatter"


def test_word_formatter_ooxml_parser_disables_external_entities():
    ooxml = (WORD_FORMATTER_ROOT / "utils" / "ooxml.py").read_text(encoding="utf-8")

    assert "XMLParser" in ooxml
    assert "resolve_entities=False" in ooxml
    assert "no_network=True" in ooxml
    assert "etree.fromstring" not in ooxml


def test_word_formatter_template_ids_use_secrets_not_random():
    template_generator = (WORD_FORMATTER_ROOT / "services" / "template_generator.py").read_text(encoding="utf-8")

    assert "import secrets" in template_generator
    assert "secrets.choice" in template_generator
    assert "import random" not in template_generator
    assert "random.choice" not in template_generator


def test_word_formatter_byok_ai_service_rejects_private_base_url():
    from app.word_formatter.routes import get_word_formatter_ai_service

    try:
        get_word_formatter_ai_service(
            {
                "polish_model": "gpt-5.4",
                "api_key": "sk-test",
                "base_url": "https://127.0.0.1/v1",
            }
        )
    except Exception as exc:
        assert "Base URL" in str(exc)
    else:
        raise AssertionError("private Base URL should be rejected")


def test_word_formatter_byok_ai_service_accepts_local_proxy_in_local_mode(monkeypatch):
    from app.word_formatter.routes import get_word_formatter_ai_service

    monkeypatch.setattr(config_module.settings, "ALLOW_LOCAL_MODEL_PROXY", True, raising=False)
    monkeypatch.setattr(config_module.settings, "SERVER_HOST", "127.0.0.1", raising=False)

    service = get_word_formatter_ai_service(
        {
            "polish_model": "gpt-5.4",
            "api_key": "sk-test",
            "base_url": "http://localhost:8317/v1",
        }
    )

    assert service.base_url == "http://localhost:8317/v1"
