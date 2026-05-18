PYTHON = python3
MODULE = -m src
MAP = maps/easy/01_linear_path.txt

.PHONY: install run debug clean lint lint-strict

install:
	@echo "Installing dependencies..."
	@uv sync

run:
	@echo "Running simulation..."
	$(PYTHON) $(MODULE) $(MAP)

debug:
	@echo "Running in debug mode..."
	$(PYTHON) -m pdb $(MODULE) 

clean:
	@echo "Cleaning cache files..."
	rm -rf src/__pycache__
	rm -rf .mypy_cache

lint:
	@echo "Running standard linting..."
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@echo "Running strict linting..."
	flake8 .
	mypy . --strict