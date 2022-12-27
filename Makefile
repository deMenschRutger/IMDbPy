test:
	ENV=testing python -m pytest

report:
	ENV=testing coverage run -m pytest
	coverage report

coverage:
	ENV=testing coverage run -m pytest
	coverage html

check:
	isort . --diff
	black . --diff
	flake8
	mypy .

lint:
	isort .
	black .