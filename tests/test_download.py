"""Tests for download functionality."""

import io
import os
from unittest.mock import Mock

import pytest
import responses
from requests import HTTPError

from autoupdate.autoupdate import create_requests_session, download_update


class TestDownloadUpdate:
    """Tests for download_update function."""

    @responses.activate
    def test_successful_download(self, temp_dir, mock_file_content):
        """Test successful file download."""
        url = "https://example.com/update.zip"
        destination = os.path.join(temp_dir, "update.zip")

        responses.add(
            responses.GET,
            url,
            body=mock_file_content,
            status=200,
            headers={"content-length": str(len(mock_file_content))},
            stream=True,
        )

        session = create_requests_session()
        result = download_update(url, destination, session)

        assert result == destination
        assert os.path.exists(destination)

        # Verify downloaded content
        with open(destination, "rb") as f:
            assert f.read() == mock_file_content

    @responses.activate
    def test_download_with_progress_callback(self, temp_dir, mock_file_content):
        """Test download with progress callback."""
        url = "https://example.com/update.zip"
        destination = os.path.join(temp_dir, "update.zip")
        progress_callback = Mock()

        responses.add(
            responses.GET,
            url,
            body=mock_file_content,
            status=200,
            headers={"content-length": str(len(mock_file_content))},
            stream=True,
        )

        session = create_requests_session()
        download_update(url, destination, session, progress_callback=progress_callback)

        # Progress callback should have been called
        assert progress_callback.called
        # Should be called at least once (exact count depends on chunk size)
        assert progress_callback.call_count >= 1

        # Last call should have total downloaded and total size
        last_call_args = progress_callback.call_args[0]
        assert len(last_call_args) == 2
        total_downloaded, total_size = last_call_args
        assert total_downloaded == len(mock_file_content)
        assert total_size == len(mock_file_content)

    @responses.activate
    def test_download_with_custom_chunk_size(self, temp_dir, mock_file_content):
        """Test download with custom chunk size."""
        url = "https://example.com/update.zip"
        destination = os.path.join(temp_dir, "update.zip")
        progress_callback = Mock()
        chunk_size = 100  # Small chunk size

        responses.add(
            responses.GET,
            url,
            body=mock_file_content,
            status=200,
            headers={"content-length": str(len(mock_file_content))},
            stream=True,
        )

        session = create_requests_session()
        download_update(
            url, destination, session, progress_callback=progress_callback, chunk_size=chunk_size
        )

        # With smaller chunks, callback should be called more times
        assert progress_callback.call_count > 1

        # File should still be correct
        with open(destination, "rb") as f:
            assert f.read() == mock_file_content

    @responses.activate
    def test_download_without_content_length(self, temp_dir, mock_file_content):
        """Test download when server doesn't provide content-length."""
        url = "https://example.com/update.zip"
        destination = os.path.join(temp_dir, "update.zip")
        progress_callback = Mock()

        # No content-length header
        responses.add(
            responses.GET,
            url,
            body=mock_file_content,
            status=200,
            stream=True,
        )

        session = create_requests_session()
        download_update(url, destination, session, progress_callback=progress_callback)

        # Download should still work
        assert os.path.exists(destination)
        with open(destination, "rb") as f:
            assert f.read() == mock_file_content

        # Callback should be called with total_size=0 (from missing header)
        assert progress_callback.called
        last_call_args = progress_callback.call_args[0]
        total_downloaded, total_size = last_call_args
        assert total_size == 0  # Missing content-length defaults to 0

    @responses.activate
    def test_download_http_error(self, temp_dir):
        """Test download with HTTP error.

        Note: File IS created (possibly empty with streaming), but error is raised.
        """
        url = "https://example.com/update.zip"
        destination = os.path.join(temp_dir, "update.zip")

        responses.add(
            responses.GET,
            url,
            json={"error": "Not found"},
            status=404,
        )

        session = create_requests_session()

        with pytest.raises(HTTPError):
            download_update(url, destination, session)

        # File IS created when opened, even though download fails
        # (Opened with 'w+b' before raise_for_status is called)
        assert os.path.exists(destination)

    @responses.activate
    def test_download_without_progress_callback(self, temp_dir, mock_file_content):
        """Test download works without progress callback."""
        url = "https://example.com/update.zip"
        destination = os.path.join(temp_dir, "update.zip")

        responses.add(
            responses.GET,
            url,
            body=mock_file_content,
            status=200,
            headers={"content-length": str(len(mock_file_content))},
            stream=True,
        )

        session = create_requests_session()
        result = download_update(url, destination, session, progress_callback=None)

        assert result == destination
        assert os.path.exists(destination)
        with open(destination, "rb") as f:
            assert f.read() == mock_file_content

    @responses.activate
    def test_download_empty_file(self, temp_dir):
        """Test downloading an empty file."""
        url = "https://example.com/empty.zip"
        destination = os.path.join(temp_dir, "empty.zip")

        responses.add(
            responses.GET,
            url,
            body=b"",
            status=200,
            headers={"content-length": "0"},
            stream=True,
        )

        session = create_requests_session()
        result = download_update(url, destination, session)

        assert result == destination
        assert os.path.exists(destination)
        assert os.path.getsize(destination) == 0

    @responses.activate
    def test_download_creates_file_in_binary_mode(self, temp_dir):
        """Test that download creates file in binary write mode."""
        url = "https://example.com/update.zip"
        destination = os.path.join(temp_dir, "update.zip")
        # Binary content with null bytes
        binary_content = b"\x00\x01\x02\xff\xfe\xfd"

        responses.add(
            responses.GET,
            url,
            body=binary_content,
            status=200,
            headers={"content-length": str(len(binary_content))},
            stream=True,
        )

        session = create_requests_session()
        download_update(url, destination, session)

        # Verify binary content is preserved
        with open(destination, "rb") as f:
            assert f.read() == binary_content
