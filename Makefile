.PHONY: test lint release

PY=python3
MOCK_ENV=BASM_RC_FILE=/tmp/sh_alias_sudo_manager_test_rc BASM_SUDOERS_PATH=/tmp/sh_alias_sudo_manager_test_sudoers

test:
	@echo "Running tests..."
	${PY} -m pytest -q

lint:
	@echo "Running flake8..."
	${PY} -m flake8

release:
	@echo "Build package..."
	${PY} -m build
	@echo "Upload package with twine (ensure TWINE_USERNAME/TWINE_PASSWORD set)"
	${PY} -m twine upload dist/*
