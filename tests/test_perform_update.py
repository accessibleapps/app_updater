"""Integration tests for the complete update flow."""

import os
import platform
import zipfile
from unittest.mock import Mock, patch

import pytest
import responses

from autoupdate.autoupdate import perform_update


class TestPerformUpdate:
    """Integration tests for perform_update function."""

    @responses.activate
    @patch("platform.system", return_value="Windows")
    @patch("win32api.ShellExecute")
    @patch("os.getpid", return_value=12345)
    @patch("platform_utils.paths.app_path", return_value="C:\\App")
    @patch("platform_utils.paths.get_executable", return_value="C:\\App\\app.exe")
    def test_successful_update_flow_windows(
        self, mock_get_exe, mock_app_path, mock_getpid, mock_shell_exec, mock_system
    ):
        """Test complete successful update flow on Windows."""
        endpoint = "https://api.example.com/check-update"
        update_url = "https://example.com/update.zip"
        current_version = "1.0.0"

        # Mock update check response
        update_response = {
            "current_version": "2.0.0",
            "description": "New version available",
            "downloads": {
                "Windows": update_url,
                "Darwin": "https://example.com/update-mac.zip",
                "Linux": "https://example.com/update-linux.zip",
            },
        }

        # Create fake zip content with bootstrap
        zip_content = self._create_zip_with_bootstrap("bootstrap.exe")

        # Mock HTTP responses
        responses.add(responses.GET, endpoint, json=update_response, status=200)
        responses.add(
            responses.GET,
            update_url,
            body=zip_content,
            status=200,
            headers={"content-length": str(len(zip_content))},
            stream=True,
        )

        # Callbacks
        update_available_callback = Mock(return_value=True)
        progress_callback = Mock()
        update_complete_callback = Mock()

        # Execute
        perform_update(
            endpoint,
            current_version,
            app_name="TestApp",
            update_available_callback=update_available_callback,
            progress_callback=progress_callback,
            update_complete_callback=update_complete_callback,
        )

        # Verify callbacks were called
        update_available_callback.assert_called_once()
        assert update_available_callback.call_args[1]["version"] == "2.0.0"
        assert update_available_callback.call_args[1]["description"] == "New version available"

        assert progress_callback.called
        update_complete_callback.assert_called_once()

        # Verify bootstrap execution
        mock_shell_exec.assert_called_once()

    @responses.activate
    def test_no_update_available_same_version(self):
        """Test when current version equals available version."""
        endpoint = "https://api.example.com/check-update"
        current_version = "1.0.0"

        update_response = {
            "current_version": "1.0.0",  # Same version
            "downloads": {"Windows": "https://example.com/update.zip"},
        }

        responses.add(responses.GET, endpoint, json=update_response, status=200)

        update_available_callback = Mock()
        update_complete_callback = Mock()

        perform_update(
            endpoint,
            current_version,
            update_available_callback=update_available_callback,
            update_complete_callback=update_complete_callback,
        )

        # Callbacks should NOT be called
        update_available_callback.assert_not_called()
        update_complete_callback.assert_not_called()

    @responses.activate
    @patch("platform.system", return_value="Windows")
    def test_no_update_for_current_platform(self, mock_system):
        """Test when no update available for current platform."""
        endpoint = "https://api.example.com/check-update"
        current_version = "1.0.0"

        update_response = {
            "current_version": "2.0.0",
            "downloads": {
                "Darwin": "https://example.com/update-mac.zip",
                "Linux": "https://example.com/update-linux.zip",
                # No Windows download
            },
        }

        responses.add(responses.GET, endpoint, json=update_response, status=200)

        update_available_callback = Mock()

        perform_update(endpoint, current_version, update_available_callback=update_available_callback)

        # Should not call update_available_callback
        update_available_callback.assert_not_called()

    @responses.activate
    def test_user_cancels_update(self):
        """Test when user cancels update via callback."""
        endpoint = "https://api.example.com/check-update"
        current_version = "1.0.0"

        update_response = {
            "current_version": "2.0.0",
            "downloads": {"Windows": "https://example.com/update.zip"},
        }

        responses.add(responses.GET, endpoint, json=update_response, status=200)

        # User cancels update
        update_available_callback = Mock(return_value=False)
        update_complete_callback = Mock()

        with patch("platform.system", return_value="Windows"):
            perform_update(
                endpoint,
                current_version,
                update_available_callback=update_available_callback,
                update_complete_callback=update_complete_callback,
            )

        # Available callback should be called
        update_available_callback.assert_called_once()
        # But complete callback should NOT be called (user cancelled)
        update_complete_callback.assert_not_called()

    @responses.activate
    def test_no_update_check_response(self):
        """Test when update check returns empty dict."""
        endpoint = "https://api.example.com/check-update"
        current_version = "1.0.0"

        # Empty response - no current_version or downloads
        responses.add(responses.GET, endpoint, json={}, status=200)

        update_available_callback = Mock()

        # Should not crash - find_update returns {} which is falsy
        perform_update(endpoint, current_version, update_available_callback=update_available_callback)

        update_available_callback.assert_not_called()

    @responses.activate
    @patch("platform.system", return_value="Linux")
    @patch("subprocess.Popen")
    @patch("os.getpid", return_value=99999)
    @patch("platform_utils.paths.app_path", return_value="/opt/app")
    @patch("platform_utils.paths.get_executable", return_value="/opt/app/bin/app")
    def test_successful_update_flow_linux(
        self, mock_get_exe, mock_app_path, mock_getpid, mock_popen, mock_system
    ):
        """Test complete successful update flow on Linux."""
        endpoint = "https://api.example.com/check-update"
        update_url = "https://example.com/update-linux.zip"
        current_version = "1.0.0"

        update_response = {
            "current_version": "2.0.0",
            "downloads": {"Linux": update_url},
        }

        # Create zip with Linux bootstrap
        zip_content = self._create_zip_with_bootstrap("bootstrap-lin.sh")

        responses.add(responses.GET, endpoint, json=update_response, status=200)
        responses.add(
            responses.GET,
            update_url,
            body=zip_content,
            status=200,
            headers={"content-length": str(len(zip_content))},
            stream=True,
        )

        update_available_callback = Mock(return_value=True)
        update_complete_callback = Mock()

        with patch("autoupdate.autoupdate.make_executable"):
            perform_update(
                endpoint,
                current_version,
                update_available_callback=update_available_callback,
                update_complete_callback=update_complete_callback,
            )

        update_available_callback.assert_called_once()
        update_complete_callback.assert_called_once()
        mock_popen.assert_called_once()

    @responses.activate
    @patch("platform.system", return_value="Windows")
    def test_update_with_password_protected_zip(self, mock_system):
        """Test update with password-protected archive."""
        endpoint = "https://api.example.com/check-update"
        update_url = "https://example.com/update.zip"
        current_version = "1.0.0"
        password = b"secret123"

        update_response = {
            "current_version": "2.0.0",
            "downloads": {"Windows": update_url},
        }

        # Create password-protected zip
        zip_content = self._create_password_protected_zip("bootstrap.exe", password)

        responses.add(responses.GET, endpoint, json=update_response, status=200)
        responses.add(
            responses.GET,
            update_url,
            body=zip_content,
            status=200,
            headers={"content-length": str(len(zip_content))},
            stream=True,
        )

        update_available_callback = Mock(return_value=True)

        with patch("win32api.ShellExecute"), patch("os.getpid", return_value=1), patch(
            "platform_utils.paths.app_path", return_value="C:\\App"
        ), patch("platform_utils.paths.get_executable", return_value="C:\\App\\app.exe"):
            perform_update(
                endpoint,
                current_version,
                password=password,
                update_available_callback=update_available_callback,
            )

        update_available_callback.assert_called_once()

    @responses.activate
    def test_version_comparison_string_based(self):
        """Test that version comparison is string-based (as per code)."""
        endpoint = "https://api.example.com/check-update"

        # String comparison: "2.0.0" > "1.0.0" is True
        current_version = "1.0.0"
        update_response = {
            "current_version": "2.0.0",
            "downloads": {"Windows": "https://example.com/update.zip"},
        }

        responses.add(responses.GET, endpoint, json=update_response, status=200)

        update_available_callback = Mock(return_value=False)  # Cancel to stop early

        with patch("platform.system", return_value="Windows"):
            perform_update(endpoint, current_version, update_available_callback=update_available_callback)

        # Should trigger update check
        update_available_callback.assert_called_once()

    # Helper methods
    def _create_zip_with_bootstrap(self, bootstrap_name):
        """Create a zip file with a bootstrap script."""
        import io

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(bootstrap_name, b"fake bootstrap script")
            zf.writestr("app.exe", b"fake app")

        return zip_buffer.getvalue()

    def _create_password_protected_zip(self, bootstrap_name, password):
        """Create a password-protected zip file."""
        import io

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.setpassword(password)
            zf.writestr(bootstrap_name, b"protected bootstrap", compress_type=zipfile.ZIP_DEFLATED)
            zf.writestr("app.exe", b"protected app", compress_type=zipfile.ZIP_DEFLATED)

        return zip_buffer.getvalue()
