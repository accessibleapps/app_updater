"""Tests for bootstrap operations."""

import os
import platform
import stat
from unittest.mock import patch

import pytest

from autoupdate.autoupdate import bootstrap_name, execute_bootstrap, make_executable, move_bootstrap


class TestBootstrapName:
    """Tests for bootstrap_name function."""

    @patch("platform.system", return_value="Windows")
    def test_bootstrap_name_windows(self, mock_system):
        """Test bootstrap name on Windows."""
        assert bootstrap_name() == "bootstrap.exe"

    @patch("platform.system", return_value="Darwin")
    def test_bootstrap_name_macos(self, mock_system):
        """Test bootstrap name on macOS."""
        assert bootstrap_name() == "bootstrap-mac.sh"

    @patch("platform.system", return_value="Linux")
    def test_bootstrap_name_linux(self, mock_system):
        """Test bootstrap name on Linux."""
        assert bootstrap_name() == "bootstrap-lin.sh"


class TestMoveBootstrap:
    """Tests for move_bootstrap function."""

    @patch("platform.system", return_value="Windows")
    def test_move_bootstrap_windows(self, mock_system, temp_dir):
        """Test moving bootstrap on Windows."""
        # Setup: create extracted directory with bootstrap
        extracted_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extracted_dir)
        bootstrap_src = os.path.join(extracted_dir, "bootstrap.exe")

        with open(bootstrap_src, "w") as f:
            f.write("fake bootstrap")

        # Execute
        result = move_bootstrap(extracted_dir)

        # Verify bootstrap moved to parent directory
        expected_path = os.path.join(temp_dir, "bootstrap.exe")
        assert result == expected_path
        assert os.path.exists(expected_path)
        assert not os.path.exists(bootstrap_src)

    @patch("platform.system", return_value="Darwin")
    def test_move_bootstrap_macos(self, mock_system, temp_dir):
        """Test moving bootstrap on macOS (from Contents/Resources)."""
        # Setup: create macOS app bundle structure
        extracted_dir = os.path.join(temp_dir, "extracted")
        resources_dir = os.path.join(extracted_dir, "Contents", "Resources")
        os.makedirs(resources_dir)
        bootstrap_src = os.path.join(resources_dir, "bootstrap-mac.sh")

        with open(bootstrap_src, "w") as f:
            f.write("#!/bin/bash\necho test")

        # Execute
        result = move_bootstrap(extracted_dir)

        # Verify bootstrap moved to working directory (parent of extracted)
        expected_path = os.path.join(temp_dir, "bootstrap-mac.sh")
        assert result == expected_path
        assert os.path.exists(expected_path)
        assert not os.path.exists(bootstrap_src)

    @patch("platform.system", return_value="Linux")
    def test_move_bootstrap_linux(self, mock_system, temp_dir):
        """Test moving bootstrap on Linux."""
        # Setup
        extracted_dir = os.path.join(temp_dir, "extracted")
        os.makedirs(extracted_dir)
        bootstrap_src = os.path.join(extracted_dir, "bootstrap-lin.sh")

        with open(bootstrap_src, "w") as f:
            f.write("#!/bin/bash\necho test")

        # Execute
        result = move_bootstrap(extracted_dir)

        # Verify
        expected_path = os.path.join(temp_dir, "bootstrap-lin.sh")
        assert result == expected_path
        assert os.path.exists(expected_path)
        assert not os.path.exists(bootstrap_src)


class TestMakeExecutable:
    """Tests for make_executable function."""

    @pytest.mark.skipif(platform.system() == "Windows", reason="Windows doesn't use Unix execute permissions")
    def test_make_executable(self, temp_dir):
        """Test making a file executable on Unix systems."""
        # Create a test file
        test_file = os.path.join(temp_dir, "test_script.sh")
        with open(test_file, "w") as f:
            f.write("#!/bin/bash\necho test")

        # Make executable
        make_executable(test_file)

        # Verify executable bit is set
        new_stat = os.stat(test_file)
        new_mode = new_stat.st_mode
        assert new_mode & stat.S_IEXEC
        # Verify file is executable
        assert os.access(test_file, os.X_OK)


class TestExecuteBootstrap:
    """Tests for execute_bootstrap function."""

    @pytest.mark.windows
    @patch("platform.system", return_value="Windows")
    @patch("win32api.ShellExecute")
    @patch("os.getpid", return_value=12345)
    @patch("platform_utils.paths.app_path", return_value="C:\\App")
    @patch("platform_utils.paths.get_executable", return_value="C:\\App\\app.exe")
    def test_execute_bootstrap_windows(
        self, mock_get_exe, mock_app_path, mock_getpid, mock_shell_exec, mock_system
    ):
        """Test executing bootstrap on Windows."""
        bootstrap_path = "C:\\temp\\bootstrap.exe"
        source_path = "C:\\temp\\update"

        execute_bootstrap(bootstrap_path, source_path)

        # Verify ShellExecute was called correctly
        mock_shell_exec.assert_called_once()
        args = mock_shell_exec.call_args[0]
        assert args[0] == 0  # hwnd
        assert args[1] == "open"  # operation
        assert args[2] == bootstrap_path  # file
        # args[3] should be the arguments string
        assert "12345" in args[3]  # PID
        assert source_path in args[3]
        assert "C:\\App" in args[3]  # app_path
        assert "C:\\App\\app.exe" in args[3]  # executable

    @pytest.mark.linux
    @patch("platform.system", return_value="Linux")
    @patch("subprocess.Popen")
    @patch("os.getpid", return_value=12345)
    @patch("platform_utils.paths.app_path", return_value="/opt/app")
    @patch("platform_utils.paths.get_executable", return_value="/opt/app/app")
    def test_execute_bootstrap_linux(
        self, mock_get_exe, mock_app_path, mock_getpid, mock_popen, mock_system, temp_dir
    ):
        """Test executing bootstrap on Linux."""
        bootstrap_path = os.path.join(temp_dir, "bootstrap-lin.sh")
        source_path = os.path.join(temp_dir, "update")

        # Create a dummy bootstrap file
        with open(bootstrap_path, "w") as f:
            f.write("#!/bin/bash\necho test")

        # Mock make_executable (it's called within execute_bootstrap)
        with patch("autoupdate.autoupdate.make_executable") as mock_make_exec:
            execute_bootstrap(bootstrap_path, source_path)

            # Verify make_executable was called
            mock_make_exec.assert_called_once_with(bootstrap_path)

        # Verify subprocess.Popen was called
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args
        assert call_args[1]["shell"] is True
        # Verify command is passed as list with single string element
        cmd = call_args[0][0]
        assert isinstance(cmd, list)
        assert len(cmd) == 1
        # The command string should contain all parts
        cmd_string = cmd[0]
        assert bootstrap_path in cmd_string
        assert "12345" in cmd_string  # PID
        assert source_path in cmd_string

    @pytest.mark.darwin
    @patch("platform.system", return_value="Darwin")
    @patch("subprocess.Popen")
    @patch("os.getpid", return_value=12345)
    @patch("platform_utils.paths.app_path", return_value="/Applications/MyApp.app")
    @patch("platform_utils.paths.get_executable", return_value="/Applications/MyApp.app/Contents/MacOS/MyApp")
    def test_execute_bootstrap_macos(
        self, mock_get_exe, mock_app_path, mock_getpid, mock_popen, mock_system, temp_dir
    ):
        """Test executing bootstrap on macOS."""
        bootstrap_path = os.path.join(temp_dir, "bootstrap-mac.sh")
        source_path = os.path.join(temp_dir, "update")

        # Create a dummy bootstrap file
        with open(bootstrap_path, "w") as f:
            f.write("#!/bin/bash\necho test")

        # Mock make_executable
        with patch("autoupdate.autoupdate.make_executable") as mock_make_exec:
            execute_bootstrap(bootstrap_path, source_path)

            # Verify make_executable was called
            mock_make_exec.assert_called_once_with(bootstrap_path)

        # Verify subprocess.Popen was called
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args
        assert call_args[1]["shell"] is True
