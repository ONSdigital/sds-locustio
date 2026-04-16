# sds-locustio

This repository contains the locust performance testing components for the SDS application.

**This readme is a guidance for testing the locust application in a sandbox environment only and is not intended for production use.**

## Initialise UV

```bash
make setup
```

## Locust performance testing with the SDS cloud service running in the GCP project

### Make sure the Project ID is specified and set in gcloud config

```bash
PROJECT_ID=<your-project-id>
gcloud config set project $PROJECT_ID
```

### Add service account to run the locust app (if not exists)

- Go to IAM page on project
- Check if service account <locustrun@PROJECT_ID.iam.gserviceaccount.com> exist
- If not, add the service account with required role by the following steps, else skip this section

#### Create locustrun service account

```bash
gcloud iam service-accounts create locustrun --project=$PROJECT_ID --description="Service account to run locust app" --display-name="locustrun"
```

#### Assign required roles to locustrun service account

Assign storage admin, firebase admin, and IAP-secured web app user role to locustrun service account.

To support Cloud Run Jobs in running Locust in headless mode, also assign Cloud Run Developer and Service Account User roles to locustrun service account.

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:locustrun@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/storage.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:locustrun@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/firebase.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:locustrun@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/iap.httpsResourceAccessor"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:locustrun@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/run.developer"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:locustrun@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/iam.serviceAccountUser"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:locustrun@$PROJECT_ID.iam.gserviceaccount.com" --role="roles/cloudscheduler.admin"
```

### Build and deploy locust performance testing as cloud run service (with UI)

```bash
make deploy-locust-service
```

#### Add permission

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

#### Access the locust app

Run on local terminal:

```bash
make run-locust-cloud
```

Then open a web browser and access URL: http://127.0.0.1:8080/

Alternatively, when running on cloud terminal:

```bash
export PROJECT_ID=$(gcloud config get project)
gcloud run services proxy locust-tasks --project $PROJECT_ID --region europe-west2
```

If run on cloud terminal, check on terminal and click the link http://127.0.0.1:8080/

### Build and deploy locust performance testing in headless mode (without UI)

Headless mode allow Locust to be run without the WebUI

#### Create a bucket to store the locust test result (if not exists)
To store the locust test result, a bucket with the name format `{PROJECT_ID}-locust-tasks-result` has to be created in the GCP project

```bash
export PROJECT_ID=$(gcloud config get project)
gcloud storage buckets create gs://$PROJECT_ID-locust-tasks-result --location=europe-west2
```

#### Set up the environment variables

Please change the variables on the makefile according to your needs. The usage of the variables is explained in the table below:

| Var Name               | Description                                                          | Value                                                                                                                                  |
| ---------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Locust_Headless        | A flag to enable headless mode                                       | true                                                                                                                                   |
| Locust_Locustfile      | Location of the locust file                                          | locustfile.py                                                                                                                          |
| Locust_Users           | Number of concurrent users                                           | User defined                                                                                                                           |
| Locust_Spawn_Rate      | Rate to spawn users                                                  | User defined                                                                                                                           |
| Locust_Run_Time        | Stop after the specified amount of time                              | User defined                                                                                                                           |
| Locust_CSV             | CSV filename that store request stats                                | locust_tasks_result                                                                                                                    |
| Locust_Test_Endpoints  | Custom parameter to select test endpoints                            | all / post_schema / get_unit_data (default)/ get_dataset_metadata / get_schema_metadata / get_schema / get_schema_v2 / get_survey_list |
| Locust_Dataset_Entries | Custom parameter to specify number of unit data in generated dataset | 1000 (default) / User defined                                                                                                          |


#### Build and deploy locust performance testing in headless mode

```bash
make deploy-locust-job
```

#### Run locust performance testing in headless mode

```bash
make run-locust-job
```

When locust job is completed, the test result will be stored in the bucket created above with the name format `{PROJECT_ID}-locust-tasks-result/{DATESTAMP}/result_stats.csv`
