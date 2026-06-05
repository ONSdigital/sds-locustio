import json
import logging
import subprocess
import time
from http import HTTPStatus

import google.oauth2.id_token
import requests
from google.cloud.storage import Bucket

from configs.config import config
from google.cloud import exceptions, storage

logger = logging.getLogger(__name__)


class LocustHelper:
    # Token expiry time is 1 hour and that will be the max time for the test at the moment
    def set_header(self) -> dict:
        """Set header for SDS requests"""
        auth_req = google.auth.transport.requests.Request()
        auth_token = google.oauth2.id_token.fetch_id_token(
            auth_req, audience=config.OAUTH_CLIENT_ID
        )

        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }

    # Get bucket from SDS
    def get_bucket(self, bucket_name: str) -> Bucket | None:
        """
        Get bucket from SDS

        Args:
            bucket_name (str): the name of the bucket
        """
        storage_client = storage.Client()
        try:
            bucket = storage_client.get_bucket(
                bucket_name,
            )
            return bucket

        except exceptions.NotFound as exc:
            logging.error(f"Error. Bucket not found: {bucket_name}.")
            return None
        except Exception as e:
            logging.error(f"Error getting bucket: {bucket_name}. Error: {e}")
            return None

    # Upload a file to SDS bucket
    def upload_file_to_bucket(self, file: str, bucket_name: str) -> int:
        """
        Uploads a file to the specified bucket.

        Args:
            file (str): the file to be uploaded
            bucket_name (str): the name of the bucket to upload the file to

        """
        storage_bucket = self.get_bucket(bucket_name)

        if storage_bucket is None:
            return -1

        try:
            blob = storage_bucket.blob(file)
            blob.upload_from_filename(
                filename=file,
                content_type="application/json",
            )

            return 1
        except exceptions as exc:
            logging.error(f"Error uploading file {file}.")
            return -1

    def wait_and_check_file_is_uploaded(
            self,
            file: str,
            bucket_name: str,
            attempts: int = 10,
            backoff: int = 0.25,
    ) -> int:
        """
        Wait and check if the file is uploaded to the bucket

        Args:
            file (str): the name of the file
            bucket_name (str): the name of the bucket
            attempts (int): the number of attempts to check for the file
            backoff (int): the backoff time between attempts

        """
        storage_bucket = self.get_bucket(bucket_name)

        while attempts != 0:
            blobs = storage_bucket.list_blobs()
            for blob in blobs:
                if blob.name == file:
                    return 1

            attempts -= 1
            time.sleep(backoff)
            backoff += backoff

        logger.error(f"Error. Uploaded file is not found: {file}.")
        return -1

    # Wait and get dataset id from SDS
    def wait_and_get_dataset_id(
        self,
        headers: dict,
        base_url: str,
        survey_id: str,
        period_id: str,
        attempts: int = 10,
        backoff: int = 0.25,
    ) -> str | None:
        """
        Wait and get dataset id from SDS

        Args:
            headers (dict): the headers for the request
            base_url (str): the base url for the request
            survey_id (str): the survey id
            period_id (str): the period id
            attempts (int): the number of attempts to make
            backoff (int): the backoff time

        Returns:
            str: the dataset id
        """
        while attempts != 0:
            response = self.get_dataset_metadata(headers, base_url, survey_id, period_id)

            if response.status_code == HTTPStatus.OK:
                for dataset_metadata in response.json():
                    return dataset_metadata["dataset_id"]

            attempts -= 1
            time.sleep(backoff)
            backoff += backoff

        logger.error(f"Error getting dataset id using survey_id: {survey_id} and period_id: {period_id}.")
        return None

    @staticmethod
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

    @staticmethod
    def force_run_schedule_job() -> None:
        """
        A script to force run the schedule job to trigger the new dataset upload function.
        """
        # Note: This is a workaround to force run the cloud scheduler to trigger the new dataset upload function.
        subprocess.run(
            [
                "python",
                "run_schedule_job.py",
                "--project_id",
                config.PROJECT_ID
            ]
        )

    def delete_all_files_from_bucket(self, bucket_name: str) -> int:
        """
        Method to delete all files from the specified bucket.

        Parameters:
            bucket_name: the name of the bucket to clean

        Returns:
            None
        """
        storage_bucket = self.get_bucket(bucket_name)

        if not storage_bucket:
            return -1

        blobs = storage_bucket.list_blobs()

        for blob in blobs:
            blob.delete()

        return 1

    # Wait and get schema guid from SDS
    def wait_and_get_schema_guid(
        self,
        headers: dict,
        base_url: str,
        survey_id: str,
        attempts: int = 10,
        backoff: int = 0.25,
    ) -> str | None:
        """
        Wait and get schema guid from SDS

        Args:
            headers (dict): the headers for the request
            base_url (str): the base url for the request
            survey_id (str): the survey id
            attempts (int): the number of attempts to make
            backoff (int): the backoff time

        Returns:
            str: the schema guid
        """
        while attempts != 0:
            response = self.get_schema_metadata(headers, base_url, survey_id)

            if response.status_code == HTTPStatus.OK:
                for schema_metadata in response.json():
                    return schema_metadata["guid"]

            attempts -= 1
            time.sleep(backoff)
            backoff += backoff

        logger.error(f"Error getting schema guid using survey_id: {survey_id}.")
        return None

    @staticmethod
    def get_schema_metadata(
        headers: dict,
        base_url: str,
        survey_id: str,
    ) -> requests.Response:
        """
        Get schema metadata from db

        Returns:
            response: the response from the API
        """
        response = requests.get(
            f"{base_url}/v1/schema_metadata?survey_id={survey_id}",
            headers=headers,
            timeout=60,
        )

        return response

    @staticmethod
    def get_dataset_metadata(
        headers: dict,
        base_url: str,
        survey_id: str,
        period_id: str,
    ) -> requests.Response:
        """
        Get dataset metadata from db

        Returns:
            response: the response from the API
        """
        response = requests.get(
            f"{base_url}/v1/dataset_metadata?survey_id={survey_id}&period_id={period_id}",
            headers=headers,
            timeout=60,
        )

        return response

    @staticmethod
    def create_schema_record_before_test(
            headers: dict,
            base_url: str,
            survey_id: str,
            payload: dict
    ) -> int:
        """Creates schema for testing purposes

        Args:
            headers (dict): the headers for the request
            base_url (str): the base url for the request
            survey_id (str): the survey id
            payload (json): json to be sent to API

        Returns:
            int: 1 if the schema record is created successfully, -1 otherwise

        """
        response = requests.post(
            f"{base_url}/v1/schema?survey_id={survey_id}",
            headers=headers,
            json=payload,
            timeout=60,
        )

        if response.status_code != HTTPStatus.OK:
            logger.error(f"Error creating schema record. Status code: {response.status_code}")
            return -1

        return 1
