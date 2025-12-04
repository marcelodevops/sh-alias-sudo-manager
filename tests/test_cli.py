import os
import sys
import subprocess
import tempfile
from pathlib import Path
import pytest

MODULE = "sh_alias_sudo_manager.cli"


def run(args, env=None):
    cmd = [sys.executable, "-m", MODULE] + args
    proc = subprocess.run(
        cmd, capture_output=True, env=env or os.environ.copy(), text=True
    )
    return proc


def test_help():
    result = run(["--help"])
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


def test_alias_add_list_remove(tmp_path, monkeypatch):
    rc_file = tmp_path / "rc_test"
    sudo_file = tmp_path / "sudo_test"
    backup_dir = tmp_path / "backups"
    env = os.environ.copy()
    env["BASM_RC_FILE"] = str(rc_file)
    env["BASM_SUDOERS_PATH"] = str(sudo_file)
    env["BASM_BACKUP_DIR"] = str(backup_dir)

    # Ensure rc exists
    rc_file.write_text("# test rc\n")
    sudo_file.write_text("# test sudoers\n")

    # Add alias
    r = run(["alias", "add", "greet", "echo hello"], env=env)
    assert r.returncode == 0
    assert "Alias 'greet' added" in r.stdout

    # List alias
    r = run(["alias", "list"], env=env)
    assert "alias greet='echo hello'" in r.stdout

    # Remove alias
    r = run(["alias", "remove", "greet"], env=env)
    assert "removed" in r.stdout.lower()

    # Confirm removed
    r = run(["alias", "list"], env=env)
    assert "greet" not in r.stdout


def test_export_add_list_remove(tmp_path):
    rc_file = tmp_path / "rc_test"
    sudo_file = tmp_path / "sudo_test"
    backup_dir = tmp_path / "backups"
    env = os.environ.copy()
    env["BASM_RC_FILE"] = str(rc_file)
    env["BASM_SUDOERS_PATH"] = str(sudo_file)
    env["BASM_BACKUP_DIR"] = str(backup_dir)

    rc_file.write_text("")
    sudo_file.write_text("# sudoers\n")

    r = run(["export", "add", "FOO", "bar baz"], env=env)
    assert "Export 'FOO' added" in r.stdout

    r = run(["export", "list"], env=env)
    assert "export FOO" in r.stdout

    r = run(["export", "remove", "FOO"], env=env)
    assert "removed" in r.stdout.lower()
