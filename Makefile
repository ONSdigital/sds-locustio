PROJECT_ID = $(shell gcloud config get project)
SANDBOX_IP_ADDRESS = $(shell gcloud compute addresses list --global  --filter=name:$(PROJECT_ID)-sds-static-lb-ip --format='value(address)' --limit=1 --project=$(PROJECT_ID))
OAUTH_CLIENT_ID = $(shell gcloud secrets versions access latest --secret=iap-secret --project=$(PROJECT_ID) | jq -r '.web.client_id')
LOCUST_HEADLESS=true
LOCUST_LOCUSTFILE=locustfile.py
LOCUST_USERS=30
LOCUST_SPAWN_RATE=10
LOCUST_RUN_TIME=1m
LOCUST_CSV=locust_tasks_result/
LOCUST_TEST_ENDPOINTS=get_unit_data
LOCUST_DATASET_ENTRIES=1000
LOCUST_PROCESSES=-1

deploy-locust-service:
	gcloud builds submit --tag europe-west2-docker.pkg.dev/${PROJECT_ID}/sds/locust-tasks:latest .
	gcloud run deploy locust-tasks --image=europe-west2-docker.pkg.dev/${PROJECT_ID}/sds/locust-tasks:latest --set-env-vars=PROJECT_ID=${PROJECT_ID},BASE_URL=https://${SANDBOX_IP_ADDRESS}.nip.io,LOCUST_HEADLESS=false,OAUTH_CLIENT_ID=${OAUTH_CLIENT_ID} --region=europe-west2 --port=8089 --service-account=locustrun@${PROJECT_ID}.iam.gserviceaccount.com --no-allow-unauthenticated --min-instances=0 --max-instances=10 --cpu=8 --memory=32Gi

run-locust-cloud:
	gcloud run services proxy locust-tasks --project ${PROJECT_ID} --region europe-west2

deploy-locust-job:
	gcloud builds submit --tag europe-west2-docker.pkg.dev/${PROJECT_ID}/sds/locust-tasks:latest .
	gcloud run jobs deploy locust-tasks --image=europe-west2-docker.pkg.dev/${PROJECT_ID}/sds/locust-tasks:latest --set-env-vars=PROJECT_ID=${PROJECT_ID},BASE_URL=https://${SANDBOX_IP_ADDRESS}.nip.io,OAUTH_CLIENT_ID=${OAUTH_CLIENT_ID},LOCUST_HEADLESS=${LOCUST_HEADLESS},LOCUST_LOCUSTFILE=${LOCUST_LOCUSTFILE},LOCUST_USERS=${LOCUST_USERS},LOCUST_SPAWN_RATE=${LOCUST_SPAWN_RATE},LOCUST_RUN_TIME=${LOCUST_RUN_TIME},LOCUST_CSV=${LOCUST_CSV},LOCUST_TEST_ENDPOINTS=${LOCUST_TEST_ENDPOINTS},LOCUST_DATASET_ENTRIES=${LOCUST_DATASET_ENTRIES},LOCUST_PROCESSES=${LOCUST_PROCESSES} --region=europe-west2 --service-account=locustrun@${PROJECT_ID}.iam.gserviceaccount.com --max-retries=0 --cpu=8 --memory=32Gi
	gcloud run jobs update locust-tasks --add-volume name=volumne_1,type=cloud-storage,bucket=${PROJECT_ID}-locust-tasks-result --add-volume-mount volume=volumne_1,mount-path=/locust_tasks_result --region=europe-west2

run-locust-job:
	gcloud run jobs execute locust-tasks --region=europe-west2

run-locust-local:
	export CONF='locust-local' && \
	export PROJECT_ID='${PROJECT_ID}' && \
	export BASE_URL='https://${SANDBOX_IP_ADDRESS}.nip.io' && \
	export OAUTH_CLIENT_ID=${OAUTH_CLIENT_ID} && \
	uv run locust -f performance_tests/locustfile.py

audit:
	uv run python -m pip_audit

lint:
	uv run python -m ruff check .

lint-fix:
	uv run python -m ruff check --fix .

setup:
	@command -v uv >/dev/null 2>&1 || { \
		echo "uv not found – installing..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	}
	uv sync

.PHONY:  bump bump-patch bump-minor bump-major
bump:
	@echo "🔼 Bumping project version (patch)..."
	uv run --only-group version-check python .github/scripts/bump_version.py patch
	@echo "🔄 Generating new lock file..."
	uv lock

bump-patch:
	@echo "🔼 Bumping project version (patch)..."
	uv run --only-group version-check python .github/scripts/bump_version.py patch
	@echo "🔄 Generating new lock file..."
	uv lock

bump-minor:
	@echo "🔼 Bumping project version (minor)..."
	uv run --only-group version-check python .github/scripts/bump_version.py minor
	@echo "🔄 Generating new lock file..."
	uv lock

bump-major:
	@echo "🔼 Bumping project version (major)..."
	uv run --only-group version-check python .github/scripts/bump_version.py major
	@echo "🔄 Generating new lock file..."
	uv lock
