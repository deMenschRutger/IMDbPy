test:
	python -m pytest

report:
	coverage run -m pytest
	coverage report

coverage:
	coverage run -m pytest
	coverage html

check:
	isort . --diff
	black . --diff
	flake8
	mypy .

lint:
	isort .
	black .