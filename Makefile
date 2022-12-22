test:
	python -m pytest

coverage:
	coverage html

check:
	isort . --diff
	black . --diff
	flake8

lint:
	isort .
	black .

types:
	mypy .