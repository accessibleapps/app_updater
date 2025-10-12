"""Tests for update checking functionality."""

import pytest
import responses
from requests import HTTPError

from autoupdate.autoupdate import create_requests_session, find_update


class TestFindUpdate:
    """Tests for find_update function."""

    @responses.activate
    def test_successful_update_check(self, sample_update_response):
        """Test successful update check returns correct data."""
        endpoint = "https://api.example.com/check-update"
        responses.add(
            responses.GET,
            endpoint,
            json=sample_update_response,
            status=200,
        )

        session = create_requests_session()
        result = find_update(endpoint, session)

        assert result == sample_update_response
        assert result["current_version"] == "2.0.0"
        assert "downloads" in result
        assert len(responses.calls) == 1

    @responses.activate
    def test_update_check_with_custom_user_agent(self, sample_update_response):
        """Test that custom user agent is sent in request."""
        endpoint = "https://api.example.com/check-update"
        responses.add(
            responses.GET,
            endpoint,
            json=sample_update_response,
            status=200,
        )

        session = create_requests_session(app_name="TestApp", version="1.0.0")
        result = find_update(endpoint, session)

        assert result == sample_update_response
        # Verify user agent was sent
        assert len(responses.calls) == 1
        assert "TestApp/'1.0.0'" in responses.calls[0].request.headers["User-Agent"]

    @responses.activate
    def test_update_check_http_error(self):
        """Test that HTTP errors are raised properly."""
        endpoint = "https://api.example.com/check-update"
        responses.add(
            responses.GET,
            endpoint,
            json={"error": "Not found"},
            status=404,
        )

        session = create_requests_session()

        with pytest.raises(HTTPError) as exc_info:
            find_update(endpoint, session)

        assert "404" in str(exc_info.value)

    @responses.activate
    def test_update_check_server_error(self):
        """Test that server errors are raised."""
        endpoint = "https://api.example.com/check-update"
        responses.add(
            responses.GET,
            endpoint,
            json={"error": "Internal server error"},
            status=500,
        )

        session = create_requests_session()

        with pytest.raises(HTTPError):
            find_update(endpoint, session)

    @responses.activate
    def test_update_check_returns_empty_response(self):
        """Test handling of empty JSON response."""
        endpoint = "https://api.example.com/check-update"
        responses.add(
            responses.GET,
            endpoint,
            json={},
            status=200,
        )

        session = create_requests_session()
        result = find_update(endpoint, session)

        assert result == {}

    @responses.activate
    def test_update_check_minimal_response(self):
        """Test handling of minimal valid response."""
        endpoint = "https://api.example.com/check-update"
        minimal_response = {
            "current_version": "1.5.0",
            "downloads": {},
        }
        responses.add(
            responses.GET,
            endpoint,
            json=minimal_response,
            status=200,
        )

        session = create_requests_session()
        result = find_update(endpoint, session)

        assert result == minimal_response
        assert result["current_version"] == "1.5.0"
        assert result["downloads"] == {}

    @responses.activate
    def test_update_check_with_description(self, sample_update_response):
        """Test that description field is properly returned."""
        endpoint = "https://api.example.com/check-update"
        responses.add(
            responses.GET,
            endpoint,
            json=sample_update_response,
            status=200,
        )

        session = create_requests_session()
        result = find_update(endpoint, session)

        assert "description" in result
        assert result["description"] == "New update available with bug fixes"

    @responses.activate
    def test_multiple_update_checks(self, sample_update_response, no_update_response):
        """Test multiple update checks with same session."""
        endpoint1 = "https://api.example.com/check-update"
        endpoint2 = "https://api.example.com/check-update-v2"

        responses.add(responses.GET, endpoint1, json=sample_update_response, status=200)
        responses.add(responses.GET, endpoint2, json=no_update_response, status=200)

        session = create_requests_session()

        result1 = find_update(endpoint1, session)
        result2 = find_update(endpoint2, session)

        assert result1["current_version"] == "2.0.0"
        assert result2["current_version"] == "1.0.0"
        assert len(responses.calls) == 2
