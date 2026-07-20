from http import HTTPStatus

from locust.env import Environment
from locust.runners import WorkerRunner

from performance_tests.configs.config import config
from performance_tests.configs.endpoints_func import generate_unique_value
from performance_tests.locust_helper import LocustHelper
from performance_tests.preprocess.preprocess_base import PreProcessBase


class PreProcessCIRSchema(PreProcessBase):
    ci_schema_guids: list[str] | None = None

    def __init__(self, header: dict, environment: Environment):
        self.header = header
        self.environment: Environment = environment
        self.worker_index = environment.runner.worker_index if isinstance(environment.runner, WorkerRunner) else None
        self.locust_helper = LocustHelper()

    def preprocess_master(self) -> int:
        response = self.locust_helper.get_cir_schema_metadata(
            headers=self.header,
            base_url=config.BASE_URL,
            survey_id=config.TEST_SURVEY_ID,
            classifier_type=config.TEST_CI_CLASSIFIER_TYPE,
            classifier_value=config.TEST_CI_CLASSIFIER_VALUE,
            language=config.TEST_CI_LANGUAGE
        )

        if response.status_code == HTTPStatus.OK:
            return self.skip("CI Schema already exists. Skipping CI Schema publish.")

        if response.status_code != HTTPStatus.NOT_FOUND:
            return self.error(f"Error retrieving CI Schema metadata: {response.status_code}")

        self.logger.info("Publishing CIR schema for testing...")

        schema_payload = self.locust_helper.load_json(config.TEST_CI_SCHEMA_FILE)

        for i in range(config.TEST_CI_SCHEMA_PUBLISH_COUNT):
            if self.locust_helper.create_cir_schema_record_before_test(
                    headers=self.header,
                    base_url=config.BASE_URL,
                    guid=generate_unique_value(config.TEST_CI_GUID),
                    validator_version=config.TEST_CI_VALIDATOR_VERSION,
                    payload=schema_payload
            ) < 0:
                return self.error("Error creating CI Schema record")

        return self.success(
            "CIR schema pre-processing completed successfully on master"
        )

    def preprocess_worker(self) -> int:
        worker_index = self.environment.runner.worker_index

        self.logger.info("Retrieving CI schema GUID")
        ci_schema_guids = self.locust_helper.wait_and_get_cir_schema_guids(
            headers=self.header,
            base_url=config.BASE_URL,
            survey_id=config.TEST_SURVEY_ID,
            classifier_type=config.TEST_CI_CLASSIFIER_TYPE,
            classifier_value=config.TEST_CI_CLASSIFIER_VALUE,
            language=config.TEST_CI_LANGUAGE,
        )

        if not ci_schema_guids:
            return self.error(f"CI Schema guids cannot be retrieved on worker {worker_index}")

        self.ci_schema_guids = ci_schema_guids
        self.logger.info(f"Test CI schema GUIDs: {self.ci_schema_guids}")

        return self.success(f"CIR schema pre-processing completed successfully on worker {worker_index}")

    def get_ci_schema_guids(self) -> list[str]:
        return self.ci_schema_guids
