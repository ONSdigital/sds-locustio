PROJECT_ID = $(shell gcloud config get project)
SDS_SANDBOX_IP_ADDRESS = $(shell gcloud compute addresses list --global  --filter=name:$(PROJECT_ID)-sds-static-lb-ip --format='value(address)' --limit=1 --project=$(PROJECT_ID))
CIR_SANDBOX_IP_ADDRESS = $(shell gcloud compute addresses list --global  --filter=name:$(PROJECT_ID)-cir-static-lb-ip --format='value(address)' --limit=1 --project=$(PROJECT_ID))
OAUTH_CLIENT_ID = $(shell gcloud secrets versions access latest --secret=iap-secret --project=$(PROJECT_ID) | jq -r '.web.client_id')
LOCUST_HEADLESS=true
LOCUST_LOCUSTFILE=locustfile.py
LOCUST_USERS=30
LOCUST_SPAWN_RATE=10
LOCUST_RUN_TIME=5m
LOCUST_CSV=locust_tasks_result/
LOCUST_TEST_ENDPOINTS=get_unit_data
LOCUST_DATASET_ENTRIES=1000
LOCUST_PROCESSES=-1

deploy-sds-locust-service:
	gcloud builds submit --tag europe-west2-docker.pkg.dev/${PROJECT_ID}/sds/locust-tasks:latest .
	gcloud run deploy locust-tasks --image=europe-west2-docker.pkg.dev/${PROJECT_ID}/sds/locust-tasks:latest --set-env-vars=APP=sds,PROJECT_ID=${PROJECT_ID},BASE_URL=https://${SDS_SANDBOX_IP_ADDRESS}.nip.io,LOCUST_HEADLESS=false,OAUTH_CLIENT_ID=${OAUTH_CLIENT_ID} --region=europe-west2 --port=8089 --service-account=locustrun@${PROJECT_ID}.iam.gserviceaccount.com --no-allow-unauthenticated --min-instances=0 --max-instances=10 --cpu=8 --memory=32Gi

# Cloud Run Admin role to user account is required to run the following command successfully.
run-locust-cloud:
	gcloud run services proxy locust-tasks --project ${PROJECT_ID} --region europe-west2

# Bucket with the name format `{PROJECT_ID}-locust-tasks-result` has to be created beforehand for the following command to run successfully.
deploy-sds-locust-job:
	gcloud builds submit --tag europe-west2-docker.pkg.dev/${PROJECT_ID}/sds/locust-tasks:latest .
	gcloud run jobs deploy locust-tasks --image=europe-west2-docker.pkg.dev/${PROJECT_ID}/sds/locust-tasks:latest --set-env-vars=APP=sds,PROJECT_ID=${PROJECT_ID},BASE_URL=https://${SDS_SANDBOX_IP_ADDRESS}.nip.io,OAUTH_CLIENT_ID=${OAUTH_CLIENT_ID},LOCUST_HEADLESS=${LOCUST_HEADLESS},LOCUST_LOCUSTFILE=${LOCUST_LOCUSTFILE},LOCUST_USERS=${LOCUST_USERS},LOCUST_SPAWN_RATE=${LOCUST_SPAWN_RATE},LOCUST_RUN_TIME=${LOCUST_RUN_TIME},LOCUST_CSV=${LOCUST_CSV},LOCUST_TEST_ENDPOINTS=${LOCUST_TEST_ENDPOINTS},LOCUST_DATASET_ENTRIES=${LOCUST_DATASET_ENTRIES},LOCUST_PROCESSES=${LOCUST_PROCESSES} --region=europe-west2 --service-account=locustrun@${PROJECT_ID}.iam.gserviceaccount.com --max-retries=0 --cpu=8 --memory=32Gi --task-timeout=300m
	gcloud run jobs update locust-tasks --add-volume name=volumne_1,type=cloud-storage,bucket=${PROJECT_ID}-locust-tasks-result --add-volume-mount volume=volumne_1,mount-path=/locust_tasks_result --region=europe-west2

deploy-cir-locust-job:
	gcloud builds submit --tag europe-west2-docker.pkg.dev/${PROJECT_ID}/cir/locust-tasks:latest .
	gcloud run jobs deploy locust-tasks --image=europe-west2-docker.pkg.dev/${PROJECT_ID}/cir/locust-tasks:latest --set-env-vars=APP=cir,PROJECT_ID=${PROJECT_ID},BASE_URL=https://${CIR_SANDBOX_IP_ADDRESS}.nip.io,OAUTH_CLIENT_ID=${OAUTH_CLIENT_ID},LOCUST_HEADLESS=${LOCUST_HEADLESS},LOCUST_LOCUSTFILE=${LOCUST_LOCUSTFILE},LOCUST_USERS=${LOCUST_USERS},LOCUST_SPAWN_RATE=${LOCUST_SPAWN_RATE},LOCUST_RUN_TIME=${LOCUST_RUN_TIME},LOCUST_CSV=${LOCUST_CSV},LOCUST_TEST_ENDPOINTS=${LOCUST_TEST_ENDPOINTS},LOCUST_DATASET_ENTRIES=${LOCUST_DATASET_ENTRIES},LOCUST_PROCESSES=${LOCUST_PROCESSES} --region=europe-west2 --service-account=locustrun@${PROJECT_ID}.iam.gserviceaccount.com --max-retries=0 --cpu=8 --memory=32Gi --task-timeout=300m
	gcloud run jobs update locust-tasks --add-volume name=volumne_1,type=cloud-storage,bucket=${PROJECT_ID}-locust-tasks-result --add-volume-mount volume=volumne_1,mount-path=/locust_tasks_result --region=europe-west2

run-locust-job:
	gcloud run jobs execute locust-tasks --region=europe-west2

# This make target is not working properly at the moment and is due to be fixed in the future.
# For now, please use the above targets to deploy locust to cloud run and execute the load tests.
run-sds-locust-local:
	export CONF='locust-local' && \
	export APP='sds' && \
	export PROJECT_ID='${PROJECT_ID}' && \
	export BASE_URL='https://${SDS_SANDBOX_IP_ADDRESS}.nip.io' && \
	export OAUTH_CLIENT_ID=${OAUTH_CLIENT_ID} && \
	uv run locust -f performance_tests/locustfile.py

run-cir-locust-local:
	export CONF='locust-local' && \
	export APP='cir' && \
	export PROJECT_ID='${PROJECT_ID}' && \
	export BASE_URL='https://${CIR_SANDBOX_IP_ADDRESS}.nip.io' && \
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
