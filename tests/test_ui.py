"""Tests for maf_app.ui.app module -- unit tests for helpers."""

from __future__ import annotations

import pytest
import httpx


class TestParsePrincipes:
    def test_normal(self) -> None:
        from maf_app.ui.app import parse_principes
        result = parse_principes("Transparence\nEquite\nRobustesse")
        assert result == ["Transparence", "Equite", "Robustesse"]

    def test_empty(self) -> None:
        from maf_app.ui.app import parse_principes
        assert parse_principes("") == []

    def test_whitespace_lines(self) -> None:
        from maf_app.ui.app import parse_principes
        result = parse_principes("  A  \n\n  B  \n  ")
        assert result == ["A", "B"]

    def test_single_line(self) -> None:
        from maf_app.ui.app import parse_principes
        assert parse_principes("Seul") == ["Seul"]


class TestCallGeneratePolicy:
    def _make_response(self, status_code: int, json_data: dict | None = None) -> httpx.Response:
        request = httpx.Request("POST", "http://test/generate-policy")
        resp = httpx.Response(status_code, json=json_data, request=request)
        return resp

    def test_success(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from maf_app.ui.app import call_generate_policy

        expected = {"policy_markdown": "# Test", "sources": []}

        def mock_post(url: str, json: dict, timeout: int) -> httpx.Response:
            return self._make_response(200, expected)

        monkeypatch.setattr(httpx, "post", mock_post)
        result = call_generate_policy({"company_name": "Test"})
        assert result == expected

    def test_connect_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from maf_app.ui.app import call_generate_policy

        def mock_post(url: str, json: dict, timeout: int) -> httpx.Response:
            raise httpx.ConnectError("Connection refused")

        monkeypatch.setattr(httpx, "post", mock_post)
        with pytest.raises(httpx.ConnectError):
            call_generate_policy({"company_name": "Test"})

    def test_http_422(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from maf_app.ui.app import call_generate_policy

        def mock_post(url: str, json: dict, timeout: int) -> httpx.Response:
            return self._make_response(422, {"detail": "invalid"})

        monkeypatch.setattr(httpx, "post", mock_post)
        with pytest.raises(httpx.HTTPStatusError):
            call_generate_policy({"company_name": "Test"})
