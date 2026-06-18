from http import HTTPStatus

from performance_tests.configs.config import config
from locust.runners import WorkerRunner
from performance_tests.locust_helper import LocustHelper
from performance_tests.preprocess.preprocess_base import PreProcessBase


class PreProcessSDSSchema(PreProcessBase):
    schema_guid = None

    def __init__(self, header: dict, environment):
        self.header = header
        self.environment = environment
        self.worker_index = environment.runner.worker_index if isinstance(environment.runner, WorkerRunner) else None
        self.locust_helper = LocustHelper()

    def preprocess_master(self) -> int:
        response = self.locust_helper.get_sds_schema_metadata(self.header, config.BASE_URL, config.TEST_SURVEY_ID)

        if response.status_code == HTTPStatus.OK:
            return self.skip("Schema already exists. Skipping schema publish.")

        if response.status_code != HTTPStatus.NOT_FOUND:
            return self.error(f"Error retrieving schema metadata: {response.status_code}")

        self.logger.info("Publishing SDS schema for testing...")

        schema_payload = self.locust_helper.load_json(config.TEST_SCHEMA_FILE)
        if self.locust_helper.create_sds_schema_record_before_test(
                self.header,
                config.BASE_URL,
                config.TEST_SURVEY_ID,
                schema_payload
        ) < 0:
            return self.error("Error creating schema record")

        return self.success(
            "SDS schema pre-processing completed successfully on master"
        )

    def preprocess_worker(self) -> int:
        worker_index = self.environment.runner.worker_index

        self.logger.info("Retrieving schema GUID")
        schema_guid = self.locust_helper.wait_and_get_sds_schema_guid(self.header, config.BASE_URL, config.TEST_SURVEY_ID)

        if not schema_guid:
            return self.error(f"Schema guid cannot be retrieved on worker {worker_index}")

        self.schema_guid = schema_guid
        self.logger.info(f"Test schema GUID: {self.schema_guid}")

        return self.success(f"SDS schema pre-processing completed successfully on worker {worker_index}")

    def get_schema_guid(self) -> str:
        return self.schema_guid
