# bash-alias-sudo-manager

# Bash Alias & Sudo Manager


A Python CLI tool to manage bash aliases, environment exports, and secure sudoers updates using `visudo`.


## Features
- Add/remove bash aliases
- Add/remove environment exports
- Safely modify sudoers entries with validation
- CLI with flags via argparse


## Installation
```bash
pip install .
```


## Usage
```bash
basmgr alias add ll "ls -l"
basmgr alias remove ll
basmgr export add JAVA_HOME /usr/lib/jvm/java-21
basmgr sudoers add "marcelo ALL=(ALL) NOPASSWD: /usr/bin/systemctl"
```

# bash-alias-sudo-manager

Small CLI to safely manage shell aliases, exports, and sudoers entries.

**Important:** this tool may modify your shell rc file (e.g. `~/.bashrc` / `~/.zshrc`) and your system sudoers file. Use with care. The tool uses `visudo` to validate sudoers changes before applying them.

## Features

- Add / remove / list `alias` entries in your shell RC file
- Add / remove / list `export` variables in your shell RC file
- Add / remove / list entries in sudoers with `visudo` validation
- Backup and restore RC file and sudoers file
- Environment overrides to make testing safe:
  - `BASM_RC_FILE` — path to RC file
  - `BASM_SUDOERS_PATH` — path to sudoers file
  - `BASM_BACKUP_DIR` — directory for backups

## Install (editable)
```bash
pip install -e .
