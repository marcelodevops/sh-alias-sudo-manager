#!/usr/bin/env python3
import argparse
import os
import subprocess
from pathlib import Path

# Detect shell rc file dynamically (bash or zsh)
SHELL = os.environ.get("SHELL", "bash")
SHELL_NAME = Path(SHELL).name
# Determine rc file for bash, zsh, or fish
if SHELL_NAME == "zsh":
    RC_FILE = Path.home() / ".zshrc"
elif SHELL_NAME == "fish":
    RC_FILE = Path.home() / ".config/fish/config.fish"
else:
    RC_FILE = Path.home() / ".bashrc"
RC_FILE = Path.home() / (".zshrc" if SHELL_NAME == "zsh" else ".bashrc")
SUDOERS_TMP = "/tmp/sudoers_edit"


def ensure_rc():
    if not RC_FILE.exists():
        RC_FILE.touch()
    if not BASHRC.exists():
        BASHRC.touch()


def add_alias(name, command):
    ensure_rc()
    line = f"alias {name}='{command}'"
    with open(RC_FILE, "a") as f:
        f.write(line)


def remove_alias(name):
    ensure_rc()
    with open(RC_FILE) as f:
        lines = f.readlines()
    with open(RC_FILE, "w") as f:
        for line in lines:
            if not line.strip().startswith(f"alias {name}="):
                f.write(line)


def add_export(var, value):
    ensure_rc()
    line = f"export {var}={value}"
    with open(RC_FILE, "a") as f:
        f.write(line)


def remove_export(var):
    ensure_rc()
    with open(RC_FILE) as f:
        lines = f.readlines()
    with open(RC_FILE, "w") as f:
        for line in lines:
            if not line.strip().startswith(f"export {var}="):
                f.write(line)


def sudoers_add(entry):
    subprocess.run(["sudo", "cp", "/etc/sudoers", SUDOERS_TMP], check=True)
    with open(SUDOERS_TMP, "a") as f:
        f.write(f"{entry}")
    result = subprocess.run(["sudo", "visudo", "-c", "-f", SUDOERS_TMP])
    if result.returncode == 0:
        subprocess.run(["sudo", "cp", SUDOERS_TMP, "/etc/sudoers"], check=True)


def main():
    parser = argparse.ArgumentParser(description="Manage bash aliases, exports, and sudoers safely.")
    sub = parser.add_subparsers(dest="cmd")

    alias = sub.add_parser("alias")
    alias_sub = alias.add_subparsers(dest="action")
    alias_add = alias_sub.add_parser("add")
    alias_add.add_argument("name")
    alias_add.add_argument("command")
    alias_rm = alias_sub.add_parser("remove")
    alias_rm.add_argument("name")

    export = sub.add_parser("export")
    exp_sub = export.add_subparsers(dest="action")
    exp_add = exp_sub.add_parser("add")
    exp_add.add_argument("var")
    exp_add.add_argument("value")
    exp_rm = exp_sub.add_parser("remove")
    exp_rm.add_argument("var")

    apply = sub.add_parser("apply", help="Reload shell configuration")

    sudo = sub.add_parser("sudoers")
    sudo_add = sudo.add_subparsers(dest="action").add_parser("add")
    sudo_add.add_argument("entry")

    args = parser.parse_args()
    if args.cmd == "alias":
        if args.action == "add": add_alias(args.name, args.command)
        elif args.action == "remove": remove_alias(args.name)
    elif args.cmd == "export":
        if args.action == "add": add_export(args.var, args.value)
        elif args.action == "remove": remove_export(args.var)
    elif args.cmd == "apply":
        # Reload current shell rc file
        subprocess.run([SHELL, "-c", f"source {RC_FILE}"], check=False)
    elif args.cmd == "sudoers":
        if args.action == "add": sudoers_add(args.entry)


if __name__ == "__main__":
    main()

