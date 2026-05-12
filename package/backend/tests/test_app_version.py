from pathlib import Path

from app.config import APP_VERSION


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_packaged_app_version_matches_release_tag():
    assert APP_VERSION == "1.0.1"


def test_admin_dashboard_fallback_version_matches_release_tag():
    admin_dashboard = (
        PROJECT_ROOT / "package" / "frontend" / "src" / "pages" / "AdminDashboard.jsx"
    ).read_text(encoding="utf-8")

    assert "const CURRENT_APP_VERSION = 'v1.0.1';" in admin_dashboard
