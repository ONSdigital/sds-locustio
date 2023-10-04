# sds-locustio

This repository contains the locust performance testing components for the SDS application.

### Setting up a virtual environment

Check that you have the correct version of Python installed and then run the following commands:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r performance_tests/requirements.txt
```

### Build the locust container and push to the GCP container registry

```bash
gcloud builds submit --tag gcr.io/$PROJECT_ID/locust-tasks:latest performance_tests/
```

### Deploy the container to cloud run

```bash
gcloud run deploy locust-tasks --image=gcr.io/$PROJECT_ID/locust-tasks:latest --set-env-vars=PROJECT_ID=$PROJECT_ID,BASE_URL=$BASE_URL,OAUTH_CLIENT_ID=$OAUTH_CLIENT_ID --region=europe-west2 --port=8089
```
