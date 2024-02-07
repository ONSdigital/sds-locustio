from config import config
import logging
import json
import time
import requests
from google.cloud import storage, exceptions

class LocustHelper:
    def __init__(self, base_url: str, headers: str, database_name: str, locust_test_id: str):
        self.base_url = base_url
        self.headers = headers
        self.database_name = database_name
        self.locust_test_id = locust_test_id

    # Delete all documents in a bucket folder
    def delete_docs(self, survey_id: str, bucket_name: str):
        """
        Deletes firestore documents

        Args:
            survey_id (str): the survey id
            bucket_name (str): the name of the bucket
        """
        storage_bucket = self.get_bucket(bucket_name)
        blobs = storage_bucket.list_blobs(prefix=survey_id)

        for blob in blobs:
            blob.delete()

    # Spin up a schema before testing
    def spin_up_schema(self, payload: str) -> None:
        """Creates schema for testing purposes

        Args:
            payload (json): json to be sent to API

        """
        try:
            requests.post(
                f"{self.base_url}/v1/schema?survey_id={self.locust_test_id}",
                headers=self.headers,
                json=payload,
                timeout=60,
            )
        except Exception as e:
            logging.error(f"Locust on start: Error spinning up schema for testing: {e}")
            raise RuntimeError(f"Locust on start: Error spinning up schema for testing: {e}")
        
    # Spin up a dataset before testing
    def spin_up_dataset(self, file: str) -> None:
        """Creates dataset for testing purposes

        Args:
            file (str): path to the dataset file

        """
        try:
            if config.OAUTH_CLIENT_ID == "localhost":
                post_sds_dataset_payload = self.load_json(file)
                self.post_dataset_to_local_endpoint(post_sds_dataset_payload)
            else:
                self.upload_file_to_bucket(file, f"{config.PROJECT_ID}-sds-europe-west2-dataset")

        except Exception as e:
            logging.error(f"Locust on start: Error spinning up dataset for testing: {e}")
            raise RuntimeError(f"Locust on start: Error spinning up dataset for testing: {e}")

    # Post dataset to SDS, only for localhost
    def post_dataset_to_local_endpoint(self, payload: str) -> None:
        """
        Publishes dataset to sds in local environment

        Args:
            payload (json): json to be sent to API

        """
        requests.post(
            f"http://localhost:3006/",
            headers=self.headers,
            json=payload,
            timeout=60,
        )

    # Set locust test id for dataset.json
    def set_locust_test_id_in_dataset(self):
        """
        Sets the locust test id in the dataset.json file
        """
        with open(config.TEST_DATASET_FILE) as f:
            dataset = json.load(f)

        dataset["survey_id"] = self.locust_test_id
        dataset["period_id"] = self.locust_test_id

        with open(config.TEST_DATASET_FILE, "w") as f:
            json.dump(dataset, f)

    # Get bucket from SDS
    def get_bucket(self, bucket_name: str) -> None:
        """
        Get bucket from SDS
        """
        storage_client = storage.Client()
        try:
            bucket = storage_client.bucket(
                bucket_name,
            )
            return bucket
        except exceptions.NotFound as e:
            logging.error(f"PT: Error getting bucket {bucket_name}.")
            raise RuntimeError(f"Error getting bucket {bucket_name}.")

    # Upload a file to SDS bucket
    def upload_file_to_bucket(self, file: str, bucket_name: str) -> None:
        """
        Uploads a file to the specified bucket.

        Args:
            file (str): the file to be uploaded
            bucket_name (str): the name of the bucket to upload the file to

        """
        storage_bucket = self.get_bucket(bucket_name)
        try:
            blob = storage_bucket.blob(file)
            blob.upload_from_filename(
                file,
                content_type="application/json",
            )
        except exceptions as e:
            raise RuntimeError(f"Error uploading file {file}.")
        
    # Get dataset id from spin up dataset
    def get_dataset_id(self, filename: str) -> str:
        """
        Get dataset id from the dataset.json file

        Args:
            filename (str): the name of the file

        Returns:
            str: the dataset id
        """
        if config.OAUTH_CLIENT_ID == "localhost":
            return self.get_dataset_id_from_local()
        else:
            return self.wait_and_get_dataset_id(filename)
        
    # Wait and get dataset id from SDS
    def wait_and_get_dataset_id(self, filename: str, attempts: int = 5, backoff: int = 0.5,):
        """
        Wait and get dataset id from SDS

        Args:
            filename (str): the name of the file
            attempts (int): the number of attempts to make
            backoff (int): the backoff time
        """
        while attempts != 0:
            response = requests.get(
                f"{self.base_url}/v1/dataset_metadata?survey_id={self.locust_test_id}&period_id={self.locust_test_id}",
                headers=self.headers,
            )

            if response.status_code == 200:
                for dataset_metadata in response.json():
                        if dataset_metadata["filename"] == filename:
                            return dataset_metadata["dataset_id"]
                        
            attempts -= 1
            time.sleep(backoff)
            backoff += backoff
                        
        raise RuntimeError(f"Error getting dataset id using filename: {filename}.")

    # Get dataset id from local endpoint
    def get_dataset_id_from_local(self):
        """
        Get dataset id from local endpoint

        Args:
            base_url (str): the base url of the SDS
        """
        
        response = requests.get(
            f"{self.base_url}/v1/dataset_metadata?survey_id={self.locust_test_id}&period_id={self.locust_test_id}"
        )

        if response.status_code == 200:
            for dataset_metadata in response.json():
                    return dataset_metadata["dataset_id"]
        else:
            raise RuntimeError(f"Error getting dataset id from local endpoint.")

    def load_json(self, filepath: str) -> dict:
        """
        Method to load json from a file.

        Parameters:
            filepath: string specifying the location of the file to be loaded.

        Returns:
            dict: the json object from the specified file.
        """
        with open(filepath) as f:
            return json.load(f)