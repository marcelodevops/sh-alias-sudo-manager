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

