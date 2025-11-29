import subprocess
import sys


def test_help():
    result = subprocess.run([sys.executable, "-m", "bash_alias_sudo_manager.cli", "--help"], capture_output=True)
    assert result.returncode == 0
    assert b"usage" in result.stdout