audit:
	python -m pip_audit

lint:
	python -m black . --check
	python -m isort . --check-only --profile black
	python -m flake8 performance_tests --max-line-length=127

lint-fix:
	black .
	isort . --profile black

setup: requirements.txt
	pip install -r requirements.txt
