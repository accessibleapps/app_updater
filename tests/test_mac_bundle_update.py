"""Exercise the same symlinks and flat Contents layout as a py2app release."""

import platform
import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest

from autoupdate.autoupdate import extract_update, move_bootstrap


def test_mac_extraction_uses_metadata_preserving_tool(monkeypatch):
    monkeypatch.setattr(platform, "system", lambda: "Darwin")
    call = Mock()
    monkeypatch.setattr(subprocess, "check_call", call)
    assert extract_update("update.zip", "destination") == "destination"
    call.assert_called_once_with(["/usr/bin/ditto", "-x", "-k", "update.zip", "destination"])


@pytest.mark.skipif(platform.system() != "Darwin", reason="Requires Mac ditto and bundle filesystem semantics")
def test_mac_archive_and_bootstrap_preserve_bundle_and_wait(tmp_path):
    incoming = tmp_path / "incoming"
    resources = incoming / "Contents" / "Resources"
    resources.mkdir(parents=True)
    script = Path(__file__).parents[1] / "autoupdate" / "bootstrappers" / "bootstrap-mac.sh"
    (resources / script.name).write_bytes(script.read_bytes())
    (resources / "new.txt").write_text("new")
    (resources / "linked.txt").symlink_to("new.txt")
    executable = incoming / "Contents" / "MacOS" / "QCast"
    executable.parent.mkdir()
    marker = tmp_path / "launched"
    executable.write_text('#!/bin/sh\ntouch "' + str(marker) + '"\n')
    executable.chmod(0o755)
    archive = tmp_path / "update.zip"
    subprocess.check_call(["/usr/bin/ditto", "-c", "-k", str(incoming), str(archive)])
    extracted = tmp_path / "extracted"
    extract_update(str(archive), str(extracted))
    bootstrap = move_bootstrap(str(extracted))
    assert (extracted / "Contents" / "Resources" / script.name).is_file()
    assert (extracted / "Contents" / "Resources" / "linked.txt").is_symlink()
    target = tmp_path / "Test App.app"
    (target / "Contents").mkdir(parents=True)
    (target / "Contents" / "stale.txt").write_text("old")
    parent = subprocess.Popen(["/bin/sleep", "30"])
    updater = subprocess.Popen([
        "/bin/bash", bootstrap, str(parent.pid), str(extracted), str(target),
        str(target / "Contents" / "MacOS" / "QCast"),
    ])
    try:
        # The parent remains alive: replacing Contents here is a real failure.
        with pytest.raises(subprocess.TimeoutExpired):
            updater.wait(timeout=1.5)
        assert (target / "Contents" / "stale.txt").exists()
    finally:
        parent.terminate()
        parent.wait()
    assert updater.wait(timeout=10) == 0
    assert marker.exists()
    assert not (target / "Contents" / "stale.txt").exists()
    assert (target / "Contents" / "Resources" / "linked.txt").is_symlink()
