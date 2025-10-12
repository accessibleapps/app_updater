"""Tests for session creation and user agent handling."""

import pytest
import requests

from autoupdate.autoupdate import create_requests_session


class TestCreateRequestsSession:
    """Tests for create_requests_session function."""

    def test_creates_session_without_app_info(self):
        """Test creating session without app name and version."""
        session = create_requests_session()

        assert isinstance(session, requests.Session)
        assert "User-Agent" in session.headers
        # Should have default requests user agent
        assert session.headers["User-Agent"].startswith("python-requests/")

    def test_creates_session_with_app_name_only(self):
        """Test creating session with app name but no version."""
        session = create_requests_session(app_name="TestApp")

        assert isinstance(session, requests.Session)
        assert "User-Agent" in session.headers
        # Should append app name with None version (no quotes around None in repr)
        assert "TestApp/None" in session.headers["User-Agent"]

    def test_creates_session_with_app_name_and_version(self):
        """Test creating session with both app name and version."""
        session = create_requests_session(app_name="TestApp", version="1.2.3")

        assert isinstance(session, requests.Session)
        assert "User-Agent" in session.headers
        # Should append app name and version
        assert "TestApp/'1.2.3'" in session.headers["User-Agent"]
        # Should still have base user agent
        assert "python-requests/" in session.headers["User-Agent"]

    def test_session_with_version_only(self):
        """Test creating session with version but no app name."""
        session = create_requests_session(version="2.0.0")

        assert isinstance(session, requests.Session)
        assert "User-Agent" in session.headers
        # Version without app name should not be appended
        # (because app_name is falsy, the if condition fails)
        assert "2.0.0" not in session.headers["User-Agent"]
        # Should only have default user agent
        assert session.headers["User-Agent"].startswith("python-requests/")

    def test_user_agent_format(self):
        """Test the exact format of the custom user agent string."""
        session = create_requests_session(app_name="MyApp", version="3.4.5")

        user_agent = session.headers["User-Agent"]

        # Should contain both parts
        assert "python-requests/" in user_agent
        assert "MyApp/'3.4.5'" in user_agent

        # Custom part should be appended with a space
        assert user_agent.endswith(" MyApp/'3.4.5'")

    def test_session_is_independent(self):
        """Test that each session is independent."""
        session1 = create_requests_session(app_name="App1", version="1.0")
        session2 = create_requests_session(app_name="App2", version="2.0")

        assert session1 is not session2
        assert "App1/'1.0'" in session1.headers["User-Agent"]
        assert "App2/'2.0'" in session2.headers["User-Agent"]
        assert "App2" not in session1.headers["User-Agent"]
        assert "App1" not in session2.headers["User-Agent"]
