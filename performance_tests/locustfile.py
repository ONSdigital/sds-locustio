import logging
import os
import subprocess

import google.oauth2.id_token
from config import config
from json_generator import JsonGenerator
from locust import HttpUser, events, task
from locust_helper import LocustHelper
from locust_test import locust_test_id

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
DATABASE_NAME = f"{config.PROJECT_ID}-{config.DATABASE}"
TEST_UNIT_DATA_IDENTIFIER = config.FIXED_IDENTIFIERS[0]
SCHEMA_BUCKET = f"{config.PROJECT_ID}-sds-europe-west2-schema"
DATASET_ID = ""

locust_helper = LocustHelper(BASE_URL, HEADERS, DATABASE_NAME, locust_test_id)
json_generator = JsonGenerator(
    locust_test_id,
    config.TEST_DATASET_FILE,
    config.DATASET_ENTRIES,
    config.FIXED_IDENTIFIERS,
)

SCHEMA_PAYLOAD = locust_helper.load_json(config.TEST_SCHEMA_FILE)
SCHEMA_GUID = "UNASSIGNED"


@events.init_command_line_parser.add_listener
def _(parser):
    # Add custom arguments to choose endpoints for testing
    parser.add_argument(
        "--test-endpoints",
        choices=["all", "exclude_post_schema", "only_post_schema", "only_unit_data"],
        default="all",
        help="Choose endpoints to test",
    )


@events.init_command_line_parser.add_listener
def _(parser):
    # Add custom arguments to choose endpoints for testing
    parser.add_argument(
        "--test-endpoints",
        choices=["all", "exclude_post_schema", "only_post_schema", "only_unit_data"],
        default="all",
        help="Choose endpoints to test",
    )


@events.test_start.add_listener
def on_test_start(**kwargs):
    """
    Function to run before the test starts
    """
    # Generate dataset file
    json_generator.generate_dataset_file()

    # Publish 1 schema for endpoint testing
    global SCHEMA_GUID
    SCHEMA_GUID = locust_helper.create_schema_record_before_test(SCHEMA_PAYLOAD)

    # Publish 1 dataset for endpoint testing
    locust_helper.create_dataset_record_before_test(config.TEST_DATASET_FILE)

    # Get dataset ID
    global DATASET_ID
    DATASET_ID = locust_helper.get_dataset_id(config.TEST_DATASET_FILE)


@events.test_stop.add_listener
def on_test_stop(**kwargs):
    """
    Function to run after the test stops
    """
    # Delete generated dataset file
    locust_helper.delete_local_file(config.TEST_DATASET_FILE)
    logging.info("dataset file for publish is deleted")

    if config.OAUTH_CLIENT_ID != "localhost":
        # Delete locust test schema files from SDS bucket
        locust_helper.delete_docs(locust_test_id, SCHEMA_BUCKET)
        logging.info("schema files deleted")

        # Delete locust test schema and dataset data from FireStore
        # Note: This is a workaround to delete data from FireStore.
        # Running the script in subprocess will avoid FireStore Client connection problem in Locust Test.
        logging.info("begin deleting firestore locust test data")
        subprocess.run(
            [
                "python",
                "delete_firestore_locust_test_data.py",
                "--project_id",
                config.PROJECT_ID,
                "--database_name",
                DATABASE_NAME,
                "--survey_id",
                locust_test_id,
            ]
        )


class PerformanceTests(HttpUser):
    host = config.BASE_URL

    def __init__(self, *args, **kwargs):
        """Override default init to save some additional class attributes"""
        super().__init__(*args, **kwargs)

        self.post_sds_schema_payload = locust_helper.load_json(config.TEST_SCHEMA_FILE)

    def on_start(self):
        super().on_start()

    def on_stop(self):
        super().on_stop()

    # Performance tests
    # Test post schema endpoint
    @task
    def http_post_sds_v1(self):
        """Performance test task for the `http_post_sds_v1` function"""
        if (
            self.environment.parsed_options.test_endpoints == "only_unit_data"
            or self.environment.parsed_options.test_endpoints == "exclude_post_schema"
        ):
            pass
        else:
            self.client.post(
                f"{BASE_URL}/v1/schema?survey_id={locust_test_id}",
                json=self.post_sds_schema_payload,
                headers=set_header(),
            )

    # Test get schema metadata endpoint
    @task
    def http_get_sds_schema_metadata_v1(self):
        """Performance test task for the `http_get_sds_schema_metadata_v1` function"""
        if (
            self.environment.parsed_options.test_endpoints == "only_unit_data"
            or self.environment.parsed_options.test_endpoints == "only_post_schema"
        ):
            pass
        else:
            self.client.get(
                f"{BASE_URL}/v1/schema_metadata?survey_id={locust_test_id}",
                headers=set_header(),
            )

    # Test get schema endpoint
    @task
    def http_get_sds_schema_v1(self):
        """Performance test task for the `http_get_sds_schema_metadata_v1` function"""
        if (
            self.environment.parsed_options.test_endpoints == "only_unit_data"
            or self.environment.parsed_options.test_endpoints == "only_post_schema"
        ):
            pass
        else:
            self.client.get(
                f"{BASE_URL}/v1/schema?survey_id={locust_test_id}",
                headers=set_header(),
            )

    # Test get schema v2 endpoint
    @task
    def http_get_sds_schema_v2(self):
        """Performance test task for the `http_get_sds_schema_metadata_v1` function"""
        if (
            self.environment.parsed_options.test_endpoints == "only_unit_data"
            or self.environment.parsed_options.test_endpoints == "only_post_schema"
        ):
            pass
        else:
            self.client.get(
                f"{BASE_URL}/v2/schema?guid={SCHEMA_GUID}",
                headers=set_header(),
            )

    # Test dataset metadata endpoint
    @task
    def http_get_sds_dataset_metadata_v1(self):
        """Performance test task for the `http_get_sds_dataset_metadata_v1` function"""
        if (
            self.environment.parsed_options.test_endpoints == "only_unit_data"
            or self.environment.parsed_options.test_endpoints == "only_post_schema"
        ):
            pass
        else:
            self.client.get(
                f"{BASE_URL}/v1/dataset_metadata?survey_id={locust_test_id}&period_id={locust_test_id}",
                headers=set_header(),
            )

    # Test unit data endpoint
    @task
    def http_get_sds_unit_data_v1(self):
        """Performance test task for the `get_unit_data_from_sds` function"""
        if self.environment.parsed_options.test_endpoints == "only_post_schema":
            pass
        else:
            self.client.get(
                f"{BASE_URL}/v1/unit_data?dataset_id={DATASET_ID}&identifier={TEST_UNIT_DATA_IDENTIFIER}",
                headers=set_header(),
            )
