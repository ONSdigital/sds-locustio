import datetime
import json
import logging
import os
import subprocess
import time
from http import HTTPStatus

import google.oauth2.id_token
import requests
from configs.config import config
from google.cloud import exceptions, storage
from google.cloud.storage import Bucket

logger = logging.getLogger(__name__)


class LocustHelper:
    sds_post_schema_url: str = "/v1/schema"
    sds_get_dataset_metadata_url: str = "/v1/dataset_metadata"
    sds_get_schema_metadata_url: str = "/v1/schema_metadata"

    cir_schema_url: str = "/collection-instruments"
    cir_schema_metadata_url: str = "/collection-instruments/metadata"

    cir_ci_survey_id_placeholder: str = "<locust_survey_id>"
    cir_ci_form_type_placeholder: str = "<locust_form_type>"
    cir_ci_language_placeholder: str = "<locust_language>"

    @staticmethod
    def set_csv_result_path() -> None:
        """
        Set the path for the csv result file if headless mode is enabled.

        # Format: /<LOCUST_CSV>/<APP>/<timestamp>/
        """
        if config.HEADLESS_MODE:
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
            subpath = config.APP + "/" + timestamp + "/result"
            os.environ["LOCUST_CSV"] = "/" + os.environ["LOCUST_CSV"] + subpath

    # Token expiry time is 1 hour and that will be the max time for the test at the moment
    @staticmethod
    def set_header() -> dict:
        """Set header for SDS requests"""
        auth_req = google.auth.transport.requests.Request()
        auth_token = google.oauth2.id_token.fetch_id_token(
            auth_req, audience=config.OAUTH_CLIENT_ID
        )

        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def get_bucket(bucket_name: str) -> Bucket | None:
        """
        Get bucket

        Args:
            bucket_name (str): the name of the bucket
        """
        storage_client = storage.Client()
        try:
            bucket = storage_client.get_bucket(
                bucket_name,
            )
            return bucket

        except exceptions.NotFound:
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
        except exceptions:
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
    def wait_and_get_sds_dataset_id(
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
            response = self.get_sds_dataset_metadata(headers, base_url, survey_id, period_id)

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
    def wait_and_get_sds_schema_guid(
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
            response = self.get_sds_schema_metadata(headers, base_url, survey_id)

            if response.status_code == HTTPStatus.OK:
                for schema_metadata in response.json():
                    return schema_metadata["guid"]

            attempts -= 1
            time.sleep(backoff)
            backoff += backoff

        logger.error(f"Error getting schema guid using survey_id: {survey_id}.")
        return None

    def get_sds_schema_metadata(
        self,
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
            f"{base_url}{self.sds_get_schema_metadata_url}?survey_id={survey_id}",
            headers=headers,
            timeout=60,
        )

        return response

    def get_sds_dataset_metadata(
        self,
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
            f"{base_url}{self.sds_get_dataset_metadata_url}?survey_id={survey_id}&period_id={period_id}",
            headers=headers,
            timeout=60,
        )

        return response

    def create_sds_schema_record_before_test(
            self,
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
            f"{base_url}{self.sds_post_schema_url}?survey_id={survey_id}",
            headers=headers,
            json=payload,
            timeout=60,
        )

        if response.status_code != HTTPStatus.OK:
            logger.error(f"Error creating schema record. Status code: {response.status_code}")
            return -1

        return 1


    def map_schema_payload(self, payload: dict) -> dict:
        """Maps schema payload with the actual values

        Returns:
            dict: the mapped payload
        """
        # replace placeholders in payload with actual values
        payload_str = json.dumps(payload)
        payload_str = payload_str.replace(self.cir_ci_survey_id_placeholder, config.TEST_SURVEY_ID)
        payload_str = payload_str.replace(self.cir_ci_form_type_placeholder, config.TEST_CI_CLASSIFIER_VALUE)
        payload_str = payload_str.replace(self.cir_ci_language_placeholder, config.TEST_CI_LANGUAGE)
        payload_mapped = json.loads(payload_str)

        return payload_mapped


    def create_cir_schema_record_before_test(
            self,
            headers: dict,
            base_url: str,
            guid: str,
            validator_version: str,
            payload: dict
    ) -> int:
        """Creates CI schema for testing purposes

        Args:
            headers (dict): the headers for the request
            base_url (str): the base url for the request
            guid (str): the guid for the CI schema
            validator_version (str): the validator version for the CI schema
            payload (json): json to be sent to API

        Returns:
            int: 1 if the CI schema record is created successfully, -1 otherwise
        """
        payload_mapped = self.map_schema_payload(payload)

        response = requests.post(
            f"{base_url}{self.cir_schema_url}?guid={guid}&validator_version={validator_version}",
            headers=headers,
            json=payload_mapped,
            timeout=60,
        )

        if response.status_code != HTTPStatus.OK:
            logger.error(f"Error creating CI schema record. Status code: {response.status_code}")
            return -1

        return 1


    def get_cir_schema_metadata(
        self,
        headers: dict,
        base_url: str,
        classifier_type: str,
        classifier_value: str,
        language: str,
        survey_id: str,
    ) -> requests.Response:
        """
        Get CI schema metadata from db

        Returns:
            response: the response from the API
        """
        response = requests.get(
            f"{base_url}{self.cir_schema_metadata_url}?classifier_type={classifier_type}&classifier_value={classifier_value}&language={language}&survey_id={survey_id}",
            headers=headers,
            timeout=60,
        )

        return response

    # Wait and get schema guid from SDS
    def wait_and_get_cir_schema_guid(
            self,
            headers: dict,
            base_url: str,
            classifier_type: str,
            classifier_value: str,
            language: str,
            survey_id: str,
            attempts: int = 10,
            backoff: int = 0.25,
    ) -> str | None:
        """
        Wait and get schema guid from SDS

        Args:
            headers (dict): the headers for the request
            base_url (str): the base url for the request
            classifier_type (str): the classifier type of the CI schema
            classifier_value (str): the classifier value of the CI schema
            language (str): the language of the CI schema
            survey_id (str): the survey id
            attempts (int): the number of attempts to make
            backoff (int): the backoff time

        Returns:
            str: the schema guid
        """
        while attempts != 0:
            response = self.get_cir_schema_metadata(
                headers=headers,
                base_url=base_url,
                survey_id=survey_id,
                classifier_type=classifier_type,
                classifier_value=classifier_value,
                language=language
            )

            if response.status_code == HTTPStatus.OK:
                for schema_metadata in response.json():
                    return schema_metadata["guid"]

            attempts -= 1
            time.sleep(backoff)
            backoff += backoff

        logger.error(f"Error getting CI schema guid using survey_id: {survey_id} form_type: {classifier_value} and language: {language}.")
        return None

    def delete_cir_schema_record_after_test(
            self,
            headers: dict,
            base_url: str,
            survey_id: str,
    ) -> int:
        """Deletes CI schema record after test

        Args:
            headers (dict): the headers for the request
            base_url (str): the base url for the request
            survey_id (str): the survey id

        Returns:
            int: 1 if the CI schema record is deleted successfully, -1 otherwise
        """

        response = requests.delete(
            f"{base_url}{self.cir_schema_url}?survey_id={survey_id}",
            headers=headers,
            timeout=300,
        )

        if response.status_code not in (HTTPStatus.OK, HTTPStatus.NOT_FOUND):
            logger.error(f"Error deleting CI schema record. Status code: {response.status_code}")
            return -1

        logger.info(f"Called delete CI schema. Status code: {response.status_code}.")

        return 1
