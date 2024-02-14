# sds-locustio

This repository contains the locust performance testing components for the SDS application.

### Setting up a virtual environment

Check that you have the correct version of Python installed and then run the following commands:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r performance_tests/requirements.txt
```

## Locust performance testing with the SDS docker version running at http://127.0.0.1:3000/

- Set the OAUTH_CLIENT_ID value as 'localhost'
- Place the 'sandbox-key.json' in the 'performance_tests' directory and set the env variable 'GOOGLE_APPLICATION_CREDENTIALS'

```bash
export OAUTH_CLIENT_ID=localhost
export DATASET_ENTRIES=100
```

### Start the locust local web server

Switch to the 'performance_tests' directory

```bash
locust -f locustfile.py
```

- Open the locust web UI at http://0.0.0.0:8089/
- Enter some parameters for the number of concurrent users and ramp up rate
- Click 'Start Swarming' to start the test

## Locust performance testing with the SDS cloud version running in the GCP project 'ons-sds-sandbox-01'

### Framework dockerized and run as a job

### Build the locust container and push to the GCP container registry

- Switch to the 'sds-locustio' directory
- Set the below env variables

```bash
PROJECT_ID=ons-sds-sandbox-01
BASE_URL=https://34.160.14.110.nip.io
OAUTH_CLIENT_ID=293516424663-6ebeaknvn4b3s6lplvo6v12trahghfsc.apps.googleusercontent.com
DATASET_ENTRIES=1000
```

```bash
gcloud builds submit --tag gcr.io/$PROJECT_ID/locust-tasks:latest performance_tests/
```

### Deploy the container to cloud run

```bash
gcloud run deploy locust-tasks --image=gcr.io/$PROJECT_ID/locust-tasks:latest --set-env-vars=PROJECT_ID=$PROJECT_ID,BASE_URL=$BASE_URL,OAUTH_CLIENT_ID=$OAUTH_CLIENT_ID,DATASET_ENTRIES=$DATASET_ENTRIES --region=europe-west2 --port=8089 --service-account=$PROJECT_ID@appspot.gserviceaccount.com