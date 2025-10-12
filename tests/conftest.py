"""Shared pytest fixtures for autoupdate tests."""

import io
import os
import tempfile
import zipfile
from unittest.mock import Mock

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_update_response():
    """Sample update check response."""
    return {
        "current_version": "2.0.0",
        "description": "New update available with bug fixes",
        "downloads": {
            "Windows": "https://example.com/app-2.0.0-win.zip",
            "Darwin": "https://example.com/app-2.0.0-mac.zip",
            "Linux": "https://example.com/app-2.0.0-linux.zip",
        },
    }


@pytest.fixture
def no_update_response():
    """Response indicating no update available."""
    return {
        "current_version": "1.0.0",
        "description": "Current version",
        "downloads": {
            "Windows": "https://example.com/app-1.0.0-win.zip",
            "Darwin": "https://example.com/app-1.0.0-mac.zip",
            "Linux": "https://example.com/app-1.0.0-linux.zip",
        },
    }


@pytest.fixture
def incomplete_update_response():
    """Update response missing current platform."""
    return {
        "current_version": "2.0.0",
        "description": "Update available",
        "downloads": {
            "OtherOS": "https://example.com/app-2.0.0-other.zip",
        },
    }


@pytest.fixture
def mock_callback():
    """Create a mock callback function."""
    return Mock(return_value=True)


@pytest.fixture
def mock_progress_callback():
    """Create a mock progress callback."""
    return Mock()


@pytest.fixture
def zip_file_path(temp_dir):
    """Create a test zip file with a dummy bootstrap script."""
    zip_path = os.path.join(temp_dir, "test_update.zip")

    # Create a zip file with test content
    with zipfile.ZipFile(zip_path, "w") as zf:
        # Add a dummy bootstrap file
        zf.writestr("bootstrap.exe", b"fake bootstrap content")
        zf.writestr("app_file.txt", b"application content")

    return zip_path


@pytest.fixture
def password_protected_zip(temp_dir):
    """Create a password-protected zip file."""
    zip_path = os.path.join(temp_dir, "protected_update.zip")
    password = b"test_password"

    # Create a password-protected zip
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.setpassword(password)
        zf.writestr("bootstrap.exe", b"protected bootstrap", compress_type=zipfile.ZIP_DEFLATED)
        zf.writestr("app_file.txt", b"protected app content", compress_type=zipfile.ZIP_DEFLATED)

    return zip_path, password


@pytest.fixture
def mock_file_content():
    """Create mock file content for download tests."""
    return b"This is test update file content" * 1000  # ~33KB


@pytest.fixture
def chunked_file_content():
    """Create chunked file content to test streaming."""
    chunks = [b"chunk1" * 100, b"chunk2" * 100, b"chunk3" * 100]
    return chunks, b"".join(chunks)


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging between tests."""
    import logging

    # Clear all handlers from the autoupdate logger
    logger = logging.getLogger("autoupdate")
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)

    yield

    # Cleanup after test
    logger.handlers.clear()
