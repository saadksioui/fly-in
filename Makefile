PYTHON = python3
MODULE = -m src
DEFAULT_MAP = maps/challenger/01_the_impossible_dream.txt

.PHONY: install run debug clean lint lint-strict

install:
	@echo "Installing dependencies..."
	@uv sync

run:
	@echo "Running simulation..."
	$(PYTHON) $(MODULE) 

debug:
	@echo "Running in debug mode..."
	$(PYTHON) -m pdb $(MODULE) 

clean:
	@echo "Cleaning cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache

lint:
	@echo "Running standard linting..."
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@echo "Running strict linting..."
	flake8 .
	mypy . --strict