from setuptools import setup


setup(
    name="sh-alias-sudo-manager",
    version="0.1.0",
    py_modules=["sh_alias_sudo_manager"],
    entry_points={
        "console_scripts": [
            "basmgr=sh_alias_sudo_manager:main",
        ],
    },
    author="Marcelo",
    description="CLI tool to manage bash aliases, exports, and sudoers safely",
)
