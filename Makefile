VENV=./venv
PYTHON = ./venv/bin/python
PYTHON3 = ./venv/bin/python3

${VENV}:
	@python -m venv ${VENV}

setup: ${VENV}

lint:
	@${PYTHON} -m flake8 .
	@${PYTHON} -m mypy . --warn-return-any \
	--warn-unused-ignores --ignore-missing-imports \
	--disallow-untyped-defs --check-untyped-defs

clean:
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@rm -rf ./dist ./.mypy_cache

fclean: clean
	@rm -rf ${VENV}