"""Tests for archive extraction functionality."""

import os
import zipfile

import pytest

from autoupdate.autoupdate import extract_update


class TestExtractUpdate:
    """Tests for extract_update function."""

    def test_extract_simple_zip(self, zip_file_path, temp_dir):
        """Test extracting a simple zip file."""
        extract_dir = os.path.join(temp_dir, "extracted")

        result = extract_update(zip_file_path, extract_dir)

        assert result == extract_dir
        assert os.path.exists(extract_dir)
        assert os.path.exists(os.path.join(extract_dir, "bootstrap.exe"))
        assert os.path.exists(os.path.join(extract_dir, "app_file.txt"))

        # Verify content
        with open(os.path.join(extract_dir, "bootstrap.exe"), "rb") as f:
            assert f.read() == b"fake bootstrap content"

    def test_extract_preserves_content(self, zip_file_path, temp_dir):
        """Test that extraction preserves file content correctly."""
        extract_dir = os.path.join(temp_dir, "extracted")

        extract_update(zip_file_path, extract_dir)

        with open(os.path.join(extract_dir, "app_file.txt"), "rb") as f:
            content = f.read()
            assert content == b"application content"

    def test_extract_password_protected_zip(self, password_protected_zip, temp_dir):
        """Test extracting password-protected zip."""
        zip_path, password = password_protected_zip
        extract_dir = os.path.join(temp_dir, "extracted_protected")

        result = extract_update(zip_path, extract_dir, password=password)

        assert result == extract_dir
        assert os.path.exists(extract_dir)
        assert os.path.exists(os.path.join(extract_dir, "bootstrap.exe"))

        # Verify content was extracted correctly
        with open(os.path.join(extract_dir, "bootstrap.exe"), "rb") as f:
            assert f.read() == b"protected bootstrap"


    def test_extract_to_nonexistent_directory(self, zip_file_path, temp_dir):
        """Test extracting to a directory that doesn't exist yet."""
        extract_dir = os.path.join(temp_dir, "new", "nested", "directory")

        # Should create the directory if it doesn't exist
        result = extract_update(zip_file_path, extract_dir)

        assert result == extract_dir
        assert os.path.exists(extract_dir)
        assert os.path.exists(os.path.join(extract_dir, "bootstrap.exe"))

    def test_extract_returns_destination_path(self, zip_file_path, temp_dir):
        """Test that extract_update returns the destination path."""
        extract_dir = os.path.join(temp_dir, "extracted")

        result = extract_update(zip_file_path, extract_dir)

        assert result == extract_dir

    def test_extract_multiple_files(self, temp_dir):
        """Test extracting zip with multiple files and directories."""
        # Create a more complex zip
        zip_path = os.path.join(temp_dir, "complex.zip")
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("bootstrap.exe", b"bootstrap")
            zf.writestr("file1.txt", b"content1")
            zf.writestr("file2.txt", b"content2")
            zf.writestr("subdir/file3.txt", b"content3")

        extract_dir = os.path.join(temp_dir, "extracted")
        extract_update(zip_path, extract_dir)

        # Verify all files extracted
        assert os.path.exists(os.path.join(extract_dir, "bootstrap.exe"))
        assert os.path.exists(os.path.join(extract_dir, "file1.txt"))
        assert os.path.exists(os.path.join(extract_dir, "file2.txt"))
        assert os.path.exists(os.path.join(extract_dir, "subdir", "file3.txt"))

    def test_extract_binary_files(self, temp_dir):
        """Test extracting binary files maintains integrity."""
        # Create zip with binary content
        binary_content = bytes(range(256))  # All byte values
        zip_path = os.path.join(temp_dir, "binary.zip")

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("bootstrap.exe", b"bootstrap")
            zf.writestr("binary_file.bin", binary_content)

        extract_dir = os.path.join(temp_dir, "extracted")
        extract_update(zip_path, extract_dir)

        # Verify binary content preserved
        with open(os.path.join(extract_dir, "binary_file.bin"), "rb") as f:
            assert f.read() == binary_content

    def test_extract_empty_zip(self, temp_dir):
        """Test extracting an empty zip file.

        Note: Python's zipfile.extractall() doesn't create the destination
        directory if the zip is empty. This is standard Python behavior.
        """
        zip_path = os.path.join(temp_dir, "empty.zip")

        # Create empty zip
        with zipfile.ZipFile(zip_path, "w"):
            pass  # Empty zip

        extract_dir = os.path.join(temp_dir, "extracted")
        result = extract_update(zip_path, extract_dir)

        assert result == extract_dir
        # Python's extractall() doesn't create directory for empty zips
        # This is expected behavior - nothing to extract, no directory needed

    def test_extract_invalid_zip_raises_error(self, temp_dir):
        """Test that extracting invalid zip file raises error."""
        # Create a file that's not a valid zip
        invalid_zip = os.path.join(temp_dir, "invalid.zip")
        with open(invalid_zip, "wb") as f:
            f.write(b"This is not a zip file")

        extract_dir = os.path.join(temp_dir, "extracted")

        with pytest.raises(zipfile.BadZipFile):
            extract_update(invalid_zip, extract_dir)
