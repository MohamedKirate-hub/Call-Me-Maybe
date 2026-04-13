FUNCTIONS_DEFINITION_FILE = data/input/functions_definition.json
INPUT_FILE = data/input/function_calling_tests.json
OUTPUT_FILE = data/output/function_calls.json

install:
	uv sync

run:
	@uv run python -m src --functions_definition ${FUNCTIONS_DEFINITION_FILE} \
	--input ${INPUT_FILE} --output ${OUTPUT_FILE}

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