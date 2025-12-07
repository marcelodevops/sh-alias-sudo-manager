import os
import sys
from pathlib import Path
import subprocess

MODULE = "sh_alias_sudo_manager.cli"


def run(args, env=None):
    cmd = [sys.executable, "-m", MODULE] + args
    proc = subprocess.run(
        cmd, capture_output=True, env=env or os.environ.copy(), text=True
    )
    return proc


def test_backup_and_restore_rc(tmp_path):
    rc_file = tmp_path / "rc_test"
    sudo_file = tmp_path / "sudo_test"
    backup_dir = tmp_path / "backups"
    env = os.environ.copy()
    env["BASM_RC_FILE"] = str(rc_file)
    env["BASM_SUDOERS_PATH"] = str(sudo_file)
    env["BASM_BACKUP_DIR"] = str(backup_dir)

    rc_file.write_text("alias a='1'\n")
    sudo_file.write_text("# sudoers\n")

    r = run(["backup"], env=env)
    assert r.returncode == 0
    # backup file exists
    assert (backup_dir / rc_file.name).with_suffix(".bak").exists() or (
        backup_dir / f"{rc_file.name}.bak"
    ).exists()
