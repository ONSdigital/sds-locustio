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
```

### Start the locust local web server

Switch to the 'performance_tests' directory

```bash
locust -f locustfile.py
```

- Open the locust web UI at http://0.0.0.0:8089/
- Enter some parameters for the number of concurrent users and ramp up rate
- Click 'Start Swarming' to start the test

## Locust performance testing with the SDS cloud version running in the GCP project

### Framework dockerized and run as a job

### Build the locust container and push to the GCP container registry

- Switch to the 'sds-locustio' directory
- Set the below env variables

```bash
PROJECT_ID=ons-sds-sandbox-01
BASE_URL=https://34.160.14.110.nip.io
OAUTH_CLIENT_ID=293516424663-6ebeaknvn4b3s6lplvo6v12trahghfsc.apps.googleusercontent.com
```

```bash
gcloud config set project $PROJECT_ID
gcloud builds submit --tag gcr.io/$PROJECT_ID/locust-tasks:latest performance_tests/
```

### Add service account to run locust app

- Go to IAM page on project
- Check if service account <locustrun@PROJECT_ID.iam.gserviceaccount.com> exist
- If not, add the service account with required role by the following steps, else skip this section

#### Create locustrun service account

```bash
gcloud iam service-accounts create locustrun --project=$PROJECT_ID --description="Service account to run locust app" --display-name="locustrun"
```

#### Assign required roles to locustrun service account

Assign storage admin, firebase admin, and IAP-secured web app user role to locustrun service account

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:locustrun@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/storage.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:locustrun@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/firebase.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:locustrun@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/iap.httpsResourceAccessor"
```

### Deploy the container to cloud run

```bash
gcloud run deploy locust-tasks --image=gcr.io/$PROJECT_ID/locust-tasks:latest --set-env-vars=PROJECT_ID=$PROJECT_ID,BASE_URL=$BASE_URL,OAUTH_CLIENT_ID=$OAUTH_CLIENT_ID --region=europe-west2 --port=8089 --service-account=locustrun@$PROJECT_ID.iam.gserviceaccount.com --no-allow-unauthenticated
```

### Add permission
Since the Locust app requires authentication, one will have to grant Cloud Run Admin role to their GCP account on the Locust app
By gcloud CLI:

- Replace <youremail@address> with your GCP account

```bash
gcloud run services add-iam-policy-binding locust-tasks --project=$PROJECT_ID --member='user:<youremail@address>' --role='roles/run.admin' --region='europe-west2'
```

Alternatively, role can be granted on GCP console:
1) Go to Cloud Run
2) Select locust-tasks app
3) Click Permission
4) Add principal <youremail@address> with role Cloud Run Admin


### Access the locust app
Run on local terminal:

```bash
gcloud run services proxy locust-tasks --project $PROJECT_ID --region europe-west2
```

Then open a web browser and access URL: http://127.0.0.1:8080/

Alternatively, when running on cloud terminal:

```bash
export PROJECT_ID=$(gcloud config get project)
gcloud run services proxy locust-tasks --project $PROJECT_ID --region europe-west2
```

If run on cloud terminal, check on terminal and click the link http://127.0.0.1:8080/
