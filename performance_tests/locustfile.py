import json
import os
import time

import google.oauth2.id_token
import requests
from locust import HttpUser, task
from locust_test import locust_test_id
from google.cloud import storage, exceptions
from config import config


BASE_URL = config.BASE_URL

if config.OAUTH_CLIENT_ID == "localhost":
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "sandbox-key.json"

def set_header():
    """Set header for SDS requests"""   
    auth_req = google.auth.transport.requests.Request()
    auth_token = google.oauth2.id_token.fetch_id_token(
        auth_req, audience=config.OAUTH_CLIENT_ID
    )
    return {"Authorization": f"Bearer {auth_token}"}

HEADERS = set_header()


# To be done - delete the documents created in the 'schemas' collection during the performance testing
def delete_docs(survey_id: str):
    """
    Deletes firestore documents

    Args:
        survey_id (str)
    """

# Post schema to SDS
def post_sds_v1(payload: str):
    """Creates schema for testing purposes

    Args:
        payload (json): json to be sent to API

    Returns:
        obj: response object
    """
    return requests.post(
        f"{BASE_URL}/v1/schema?survey_id={locust_test_id}",
        headers=HEADERS,
        json=payload,
        timeout=60,
    )

# Set locust test id for dataset.json
def set_locust_test_id_in_dataset():
    """"""
    with open(config.TEST_DATASET_FILE) as f:
        dataset = json.load(f)

    dataset["survey_id"] = locust_test_id
    dataset["period_id"] = locust_test_id

    with open(config.TEST_DATASET_FILE, "w") as f:
        json.dump(dataset, f)

# Get bucket from SDS
def get_bucket(bucket_name: str):
    """"""
    storage_client = storage.Client()
    try:
        bucket = storage_client.bucket(
            bucket_name,
        )
        return bucket
    except exceptions.NotFound as e:
        raise RuntimeError(f"Error getting bucket {bucket_name}.")

# Upload dataset file to SDS bucket
def upload_file_to_bucket(file: str, bucket_name: str):
    """"""
    storage_bucket = get_bucket(bucket_name)
    try:
        blob = storage_bucket.blob(file)
        blob.upload_from_filename(
            file,
            content_type="application/json",
        )
    except exceptions as e:
        raise RuntimeError(f"Error uploading file {file}.")
    
# Get dataset id for unit data endpoint testing
def get_dataset_id(base_url: str, headers: str, filename: str, attempts: int = 5, backoff: int = 0.5,):
    """"""
    while attempts != 0:
        response = requests.get(
            f"{base_url}/v1/dataset_metadata?survey_id={locust_test_id}&period_id={locust_test_id}",
            headers=headers,
        )

        if response.status_code == 200:
            for dataset_metadata in response.json():
                    if dataset_metadata["filename"] == filename:
                        return dataset_metadata["dataset_id"]
                    
        attempts -= 1
        time.sleep(backoff)
        backoff += backoff
                    
    raise RuntimeError(f"Error getting dataset id using filename: {filename}.")


def load_json(filepath: str) -> dict:
    """
    Method to load json from a file.

    Parameters:
        filepath: string specifying the location of the file to be loaded.

    Returns:
        dict: the json object from the specified file.
    """
    with open(filepath) as f:
        return json.load(f)


class PerformanceTests(HttpUser):
    host = config.BASE_URL

    def __init__(self, *args, **kwargs):
        """Override default init to save some additional class attributes"""
        super().__init__(*args, **kwargs)

        self.post_sds_schema_payload = load_json(config.TEST_SCHEMA_FILE)
        self.request_headers = HEADERS

    def on_start(self):
        super().on_start()
        # Publish 1 schema for endpoint testing
        post_sds_v1(self.post_sds_schema_payload)
        # Set locust test id for dataset.json
        set_locust_test_id_in_dataset()
        # Publish 1 dataset for endpoint testing
        upload_file_to_bucket(config.TEST_DATASET_FILE, f"{config.PROJECT_ID}-sds-europe-west2-dataset")
        # Get dataset id
        self.dataset_id = get_dataset_id(BASE_URL, HEADERS, config.TEST_DATASET_FILE)

    def on_stop(self):
        super().on_stop()
        # Read schema metadata from FireStore where survey_id = locust_test_id
        # Retrieve the GUID from schema metadata
        # Delete created schema files from schema bucket where filename = GUID.json
        # Delete inserted schema data from FireStore where survey_id = locust_test_id
        # Delete inserted dataset and sub collection (unit data) from FireStore where survey_id = locust_test_id

    ### Performance tests ###

    # Test post schema endpoint
    @task
    def http_post_sds_v1(self):
        """Performance test task for the `http_post_sds_v1` function"""
        self.client.post(
            f"{BASE_URL}/v1/schema?survey_id={locust_test_id}",
            json=self.post_sds_schema_payload,
            headers=set_header(),
        )

    # Test get schema metadata endpoint
    @task
    def http_get_sds_schema_metadata_v1(self):
        """Performance test task for the `http_get_sds_schema_metadata_v1` function"""
        self.client.get(
            f"{BASE_URL}/v1/schema_metadata?survey_id={locust_test_id}",
            headers=set_header(),
        )

    # Test get schema endpoint
    @task
    def http_get_sds_schema_v1(self):
        """Performance test task for the `http_get_sds_schema_metadata_v1` function"""
        self.client.get(
            f"{BASE_URL}/v1/schema?survey_id={locust_test_id}",
            headers=set_header(),
        )

    # Test get schema v2 endpoint
        # Wait to be done - get schema v2 endpoint is not ready yet

    # Test dataset metadata endpoint
    @task
    def http_get_sds_dataset_metadata_v1(self):
        """"""
        self.client.get(
            f"{BASE_URL}/v1/dataset_metadata?survey_id={locust_test_id}&period_id={locust_test_id}",
            headers=set_header(),
        )

    # Test unit data endpoint
    @task
    def http_get_sds_unit_data_v1(self):
        """Performance test task for the `get_unit_data_from_sds` function"""
        self.client.get(
            f"{BASE_URL}/v1/unit_data?dataset_id={self.dataset_id}&identifier=43532",
            headers=set_header(),
        )

    # Test publish dataset endpoint
        # Wait to be done - publish dataset endpoint is not ready yet
