from http import HTTPStatus

from configs.config import config
from json_generator import JsonGenerator
from locust.runners import WorkerRunner
from locust_test import FIXED_IDENTIFIERS
from locust_helper import LocustHelper

from preprocess.preprocess_base import PreProcessBase


class PreProcessSDSDataset(PreProcessBase):
    dataset_bucket_name = f"{config.PROJECT_ID}-sds-europe-west2-dataset"
    dataset_id = None

    def __init__(self, header: dict, environment):
        self.header = header
        self.environment = environment
        self.worker_index = environment.runner.worker_index if isinstance(environment.runner, WorkerRunner) else None
        self.locust_helper = LocustHelper()

    def preprocess_master(self) -> int:

        response = self.locust_helper.get_sds_dataset_metadata(
            self.header, config.BASE_URL, config.TEST_SURVEY_ID, config.TEST_PERIOD_ID
        )


        if response.status_code == HTTPStatus.OK:
            return self.skip("Dataset already exists. Skipping dataset generation.")

        if response.status_code != HTTPStatus.NOT_FOUND:
            return self.error(f"Error retrieving dataset metadata: {response.status_code}")


        self.logger.info("Generating dataset file...")

        json_generator = JsonGenerator(
            config.TEST_SURVEY_ID,
            config.TEST_DATASET_FILE,
            FIXED_IDENTIFIERS,
        )

        dataset_entries = self.environment.parsed_options.dataset_entries

        if json_generator.generate_dataset_file(dataset_entries) < 0:
            return self.error("Error generating dataset file")

        # Publish 1 dataset for endpoint testing
        self.logger.info("Publishing SDS dataset for testing...")

        self.logger.info("Cleaning up dataset bucket...")
        if self.locust_helper.delete_all_files_from_bucket(
            self.dataset_bucket_name
        ) < 0:
            return self.error("Error cleaning up dataset bucket")

        self.logger.info("Uploading file to bucket...")
        if self.locust_helper.upload_file_to_bucket(
            config.TEST_DATASET_FILE, self.dataset_bucket_name
        ) < 0:
            return self.error("Error uploading file to bucket")

        self.logger.info("Wait and check if file is uploaded...")
        if self.locust_helper.wait_and_check_file_is_uploaded(
            config.TEST_DATASET_FILE, self.dataset_bucket_name
        ) < 0:
            return self.error("Error waiting for file to be uploaded")

        self.logger.info("Force running schedule job to publish dataset...")
        self.locust_helper.force_run_schedule_job()

        return self.success(
            f"SDS dataset pre-processing completed successfully on master"
        )

    def preprocess_worker(self) -> int:
        worker_index = self.environment.runner.worker_index

        self.logger.info(f"Retrieving dataset ID via SDS Dataset preprocessor on worker {worker_index}")

        dataset_id = self.locust_helper.wait_and_get_sds_dataset_id(
            self.header, config.BASE_URL, config.TEST_SURVEY_ID, config.TEST_PERIOD_ID
        )

        if not dataset_id:
            return self.error(f"Dataset ID cannot be retrieved on worker {worker_index}")

        self.dataset_id = dataset_id
        self.logger.info(f"Dataset ID successfully retrieved: {self.dataset_id}")

        return self.success(f"SDS dataset pre-processing completed successfully on worker {worker_index}")

    def get_dataset_id(self) -> str | None:
        return self.dataset_id