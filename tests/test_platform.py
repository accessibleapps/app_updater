"""Tests for platform-specific logic across Windows, macOS, and Linux."""

import os
from unittest.mock import patch

import pytest

from autoupdate.autoupdate import bootstrap_name, move_bootstrap


class TestPlatformSpecificBootstrapSelection:
    """Test that correct bootstrap is selected for each platform."""

    @pytest.mark.parametrize(
        "platform_name,expected_bootstrap",
        [
            ("Windows", "bootstrap.exe"),
            ("Darwin", "bootstrap-mac.sh"),
            ("Linux", "bootstrap-lin.sh"),
        ],
    )
    def test_bootstrap_selection_by_platform(self, platform_name, expected_bootstrap):
        """Test bootstrap name selection for each platform."""
        with patch("platform.system", return_value=platform_name):
            assert bootstrap_name() == expected_bootstrap


class TestPlatformSpecificPathHandling:
    """Test platform-specific path handling."""

    @patch("platform.system", return_value="Darwin")
    def test_macos_uses_resources_directory(self, mock_system, temp_dir):
        """Test that macOS looks for bootstrap in Contents/Resources."""
        # Create macOS bundle structure
        extracted_dir = os.path.join(temp_dir, "MyApp.app")
        resources_dir = os.path.join(extracted_dir, "Contents", "Resources")
        os.makedirs(resources_dir)

        # Create bootstrap in Resources
        bootstrap_src = os.path.join(resources_dir, "bootstrap-mac.sh")
        with open(bootstrap_src, "w") as f:
            f.write("#!/bin/bash")

        # Move bootstrap
        result = move_bootstrap(extracted_dir)

        # Should move to parent of extracted_dir
        expected_dest = os.path.join(temp_dir, "bootstrap-mac.sh")
        assert result == expected_dest
        assert os.path.exists(expected_dest)

    @patch("platform.system", return_value="Windows")
    def test_windows_uses_flat_structure(self, mock_system, temp_dir):
        """Test that Windows looks for bootstrap in root directory."""
        extracted_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extracted_dir)

        # Create bootstrap in root
        bootstrap_src = os.path.join(extracted_dir, "bootstrap.exe")
        with open(bootstrap_src, "wb") as f:
            f.write(b"MZ")  # Fake PE header

        # Move bootstrap
        result = move_bootstrap(extracted_dir)

        # Should move to parent
        expected_dest = os.path.join(temp_dir, "bootstrap.exe")
        assert result == expected_dest
        assert os.path.exists(expected_dest)

    @patch("platform.system", return_value="Linux")
    def test_linux_uses_flat_structure(self, mock_system, temp_dir):
        """Test that Linux looks for bootstrap in root directory."""
        extracted_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extracted_dir)

        # Create bootstrap in root
        bootstrap_src = os.path.join(extracted_dir, "bootstrap-lin.sh")
        with open(bootstrap_src, "w") as f:
            f.write("#!/bin/bash")

        # Move bootstrap
        result = move_bootstrap(extracted_dir)

        # Should move to parent
        expected_dest = os.path.join(temp_dir, "bootstrap-lin.sh")
        assert result == expected_dest
        assert os.path.exists(expected_dest)


class TestCrossPlatformUpdateFlow:
    """Test that update flow logic handles all platforms correctly."""

    @pytest.mark.parametrize(
        "platform_name,bootstrap_file",
        [
            ("Windows", "bootstrap.exe"),
            ("Darwin", "bootstrap-mac.sh"),
            ("Linux", "bootstrap-lin.sh"),
        ],
    )
    def test_bootstrap_file_exists_for_platform(self, platform_name, bootstrap_file, temp_dir):
        """Test that correct bootstrap file is expected for each platform."""
        with patch("platform.system", return_value=platform_name):
            # Setup directory
            extracted_dir = os.path.join(temp_dir, "extracted")

            if platform_name == "Darwin":
                # macOS structure
                resources_dir = os.path.join(extracted_dir, "Contents", "Resources")
                os.makedirs(resources_dir)
                bootstrap_path = os.path.join(resources_dir, bootstrap_file)
            else:
                # Windows/Linux structure
                os.makedirs(extracted_dir)
                bootstrap_path = os.path.join(extracted_dir, bootstrap_file)

            # Create bootstrap
            with open(bootstrap_path, "w") as f:
                f.write("bootstrap content")

            # Move and verify
            result = move_bootstrap(extracted_dir)
            expected = os.path.join(temp_dir, bootstrap_file)
            assert result == expected
            assert os.path.exists(expected)
