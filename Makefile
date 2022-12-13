check:
	isort . --diff
	black . --diff
	flake8

lint:
	isort .
	black .