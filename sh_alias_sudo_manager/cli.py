#!/usr/bin/env python3
"""
sh_alias_sudo_manager.cli
Safe manager for shell aliases, exports, and sudoers entries.

Environment overrides (useful for tests):
  BASM_RC_FILE          - path to shell rc file to use instead of ~/.bashrc or ~/.zshrc
  BASM_SUDOERS_PATH     - path to sudoers file to use instead of /etc/sudoers
  BASM_BACKUP_DIR       - directory to store backups (defaults to /tmp)
"""
from __future__ import annotations
import argparse
import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional

# Detect shell rc file but allow override for tests
SHELL = os.environ.get("SHELL", "/bin/bash")
SHELL_NAME = Path(SHELL).name

_default_rc = Path.home() / (".zshrc" if SHELL_NAME == "zsh" else ".bashrc")
RC_FILE = Path(os.environ.get("BASM_RC_FILE", str(_default_rc)))

# Sudoers path can be overridden for testing
SUDOERS_PATH = Path(os.environ.get("BASM_SUDOERS_PATH", "/etc/sudoers"))

# Backup directory
BACKUP_DIR = Path(os.environ.get("BASM_BACKUP_DIR", "/tmp"))


def ensure_rc():
    if not RC_FILE.exists():
        RC_FILE.parent.mkdir(parents=True, exist_ok=True)
        RC_FILE.touch()


### -- Alias functions ---------------------------------------------------------


def add_alias(name: str, command: str):
    ensure_rc()
    with open(RC_FILE, "a", encoding="utf-8") as f:
        f.write(f"alias {name}='{command}'\n")
    print(f"Alias '{name}' added to {RC_FILE}")


def list_aliases():
    ensure_rc()
    with open(RC_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("alias "):
                print(line.rstrip())


def remove_alias(name: str):
    ensure_rc()
    with open(RC_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(RC_FILE, "w", encoding="utf-8") as f:
        for line in lines:
            if not line.strip().startswith(f"alias {name}="):
                f.write(line)
    print(f"Alias '{name}' removed (if present) from {RC_FILE}")


### -- Export functions --------------------------------------------------------


def add_export(var: str, value: str):
    ensure_rc()
    # Quote the value if it contains spaces
    if " " in value:
        value = f'"{value}"'
    with open(RC_FILE, "a", encoding="utf-8") as f:
        f.write(f"export {var}={value}\n")
    print(f"Export '{var}' added to {RC_FILE}")


def list_exports():
    ensure_rc()
    with open(RC_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("export "):
                print(line.rstrip())


def remove_export(var: str):
    ensure_rc()
    with open(RC_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(RC_FILE, "w", encoding="utf-8") as f:
        for line in lines:
            if not line.strip().startswith(f"export {var}="):
                f.write(line)
    print(f"Export '{var}' removed (if present) from {RC_FILE}")


### -- Sudoers functions -------------------------------------------------------


def _copy_sudoers_to_temp() -> Path:
    tmp = Path(tempfile.mktemp(prefix="sudoers_"))
    # copy preserving permissions; use shutil.copy2
    shutil.copy2(SUDOERS_PATH, tmp)
    return tmp


def sudoers_list():
    with open(SUDOERS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            # Very simple heuristic: non-empty non-comment lines are shown.
            if stripped and not stripped.startswith("#"):
                print(line.rstrip())


def sudoers_add(entry: str):
    tmp = _copy_sudoers_to_temp()
    with open(tmp, "a", encoding="utf-8") as f:
        f.write(f"\n{entry}\n")
    # Validate with visudo using -c -f <file>
    result = subprocess.run(["sudo", "visudo", "-c", "-f", str(tmp)])
    if result.returncode == 0:
        print("Validation OK. Applying changes to sudoers (will require sudo).")
        subprocess.run(["sudo", "cp", str(tmp), str(SUDOERS_PATH)], check=True)
        print("Applied.")
    else:
        print("visudo validation failed. Changes not applied.")
    tmp.unlink(missing_ok=True)


def sudoers_remove(pattern: str):
    tmp = _copy_sudoers_to_temp()
    with open(tmp, "r", encoding="utf-8") as f:
        lines = f.readlines()
    with open(tmp, "w", encoding="utf-8") as f:
        for line in lines:
            if pattern not in line:
                f.write(line)
    result = subprocess.run(["sudo", "visudo", "-c", "-f", str(tmp)])
    if result.returncode == 0:
        print("Validation OK. Applying removal to sudoers (will require sudo).")
        subprocess.run(["sudo", "cp", str(tmp), str(SUDOERS_PATH)], check=True)
        print("Applied removal.")
    else:
        print("visudo validation failed after attempted removal. No changes applied.")
    tmp.unlink(missing_ok=True)


### -- Backup & Restore --------------------------------------------------------


def backup(rc: bool = True, sudoers: bool = True) -> dict:
    """
    Create backups of RC_FILE and/or SUDOERS_PATH in BACKUP_DIR.
    Returns a dict mapping 'rc'/'sudoers' to backup file paths.
    """
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    created = {}
    if rc:
        ensure_rc()
        rc_backup = BACKUP_DIR / f"{RC_FILE.name}.bak"
        shutil.copy2(RC_FILE, rc_backup)
        created["rc"] = str(rc_backup)
        print(f"Backed up {RC_FILE} -> {rc_backup}")
    if sudoers:
        sudo_backup = BACKUP_DIR / f"{SUDOERS_PATH.name}.bak"
        shutil.copy2(SUDOERS_PATH, sudo_backup)
        created["sudoers"] = str(sudo_backup)
        print(f"Backed up {SUDOERS_PATH} -> {sudo_backup}")
    return created


def restore(rc: bool = True, sudoers: bool = True) -> dict:
    """
    Restore backups from BACKUP_DIR. Returns dict of restored files.
    """
    restored = {}
    if rc:
        rc_backup = BACKUP_DIR / f"{RC_FILE.name}.bak"
        if rc_backup.exists():
            shutil.copy2(rc_backup, RC_FILE)
            restored["rc"] = str(RC_FILE)
            print(f"Restored {RC_FILE} from {rc_backup}")
        else:
            print(f"No rc backup found at {rc_backup}")
    if sudoers:
        sudo_backup = BACKUP_DIR / f"{SUDOERS_PATH.name}.bak"
        if sudo_backup.exists():
            # Validate before writing
            tmp = Path(tempfile.mktemp(prefix="sudoers_restore_"))
            shutil.copy2(sudo_backup, tmp)
            result = subprocess.run(["sudo", "visudo", "-c", "-f", str(tmp)])
            if result.returncode == 0:
                subprocess.run(["sudo", "cp", str(tmp), str(SUDOERS_PATH)], check=True)
                restored["sudoers"] = str(SUDOERS_PATH)
                print(f"Restored {SUDOERS_PATH} from {sudo_backup}")
            else:
                print("Backup sudoers file failed visudo validation; not restored.")
            tmp.unlink(missing_ok=True)
        else:
            print(f"No sudoers backup found at {sudo_backup}")
    return restored


### -- CLI wiring --------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage shell aliases, exports, and sudoers safely."
    )
    sub = parser.add_subparsers(dest="cmd")

    # alias
    alias = sub.add_parser("alias")
    alias_sub = alias.add_subparsers(dest="action")
    alias_sub.add_parser("list")
    alias_add = alias_sub.add_parser("add")
    alias_add.add_argument("name")
    alias_add.add_argument("command")
    alias_rm = alias_sub.add_parser("remove")
    alias_rm.add_argument("name")

    # export
    export = sub.add_parser("export")
    exp_sub = export.add_subparsers(dest="action")
    exp_sub.add_parser("list")
    exp_add = exp_sub.add_parser("add")
    exp_add.add_argument("var")
    exp_add.add_argument("value")
    exp_rm = exp_sub.add_parser("remove")
    exp_rm.add_argument("var")

    # apply
    sub.add_parser("apply", help="Reload shell configuration")

    # sudoers
    sudo = sub.add_parser("sudoers")
    sudo_sub = sudo.add_subparsers(dest="action")
    sudo_sub.add_parser("list")
    sudo_add = sudo_sub.add_parser("add")
    sudo_add.add_argument("entry")
    sudo_rm = sudo_sub.add_parser("remove")
    sudo_rm.add_argument("pattern")

    # backup/restore
    back = sub.add_parser("backup", help="Backup RC file and/or sudoers to backup dir")
    back.add_argument(
        "--no-rc", action="store_false", dest="rc", help="Don't backup RC file"
    )
    back.add_argument(
        "--no-sudoers",
        action="store_false",
        dest="sudoers",
        help="Don't backup sudoers",
    )

    restore_p = sub.add_parser(
        "restore", help="Restore RC file and/or sudoers from backup dir"
    )
    restore_p.add_argument(
        "--no-rc", action="store_false", dest="rc", help="Don't restore RC file"
    )
    restore_p.add_argument(
        "--no-sudoers",
        action="store_false",
        dest="sudoers",
        help="Don't restore sudoers",
    )

    return parser


def main(argv: Optional[list[str]] = None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "alias":
        if args.action == "add":
            add_alias(args.name, args.command)
        elif args.action == "remove":
            remove_alias(args.name)
        elif args.action == "list":
            list_aliases()

    elif args.cmd == "export":
        if args.action == "add":
            add_export(args.var, args.value)
        elif args.action == "remove":
            remove_export(args.var)
        elif args.action == "list":
            list_exports()

    elif args.cmd == "apply":
        # this will spawn a shell to source the rc; may not affect current process
        subprocess.run([SHELL, "-c", f"source {RC_FILE}"], check=False)

    elif args.cmd == "sudoers":
        if args.action == "add":
            sudoers_add(args.entry)
        elif args.action == "remove":
            sudoers_remove(args.pattern)
        elif args.action == "list":
            sudoers_list()

    elif args.cmd == "backup":
        backup(rc=args.rc, sudoers=args.sudoers)

    elif args.cmd == "restore":
        restore(rc=args.rc, sudoers=args.sudoers)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
