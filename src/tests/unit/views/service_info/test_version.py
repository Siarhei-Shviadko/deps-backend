import pytest


def test_get_service_version__200(client, app):
    response = client.get("/api/document/service-info/version")
    data = response.json()
    service_version_info = app.container.config.service_version()

    assert response.status_code == 200
    assert data["buildTag"] == service_version_info["tag"]
    assert data["buildDate"] == service_version_info["date"]
    assert data["commitHash"] == service_version_info["hash"]
