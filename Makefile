# Global Variables
PROJECT_ID=ons-sds-sandbox-01
BASE_URL=https://34.160.14.110.nip.io
OAUTH_CLIENT_ID=293516424663-6ebeaknvn4b3s6lplvo6v12trahghfsc.apps.googleusercontent.com

audit:
	python -m pip_audit
	
lint:
	black . --check
	isort . --check-only --profile black
	flake8 performance_tests --max-line-length=127

lint-fix:
	black .
	isort . --profile black

setup: requirements.txt
	pip install -r requirements.txt
