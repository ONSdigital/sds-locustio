import datetime
import logging
import os

from config import config
from json_generator import JsonGenerator
from locust import FastHttpUser, between, events, task
from locust.runners import MasterRunner
from locust_helper import LocustHelper
from locust_test import locust_test_id

# Set up logging

logger = logging.getLogger(__name__)

# Set global variables

BASE_URL = config.BASE_URL
HEADER = ""
DATABASE_NAME = f"{config.PROJECT_ID}-{config.DATABASE}"
TEST_UNIT_DATA_IDENTIFIER = config.FIXED_IDENTIFIERS[0]
SCHEMA_BUCKET = f"{config.PROJECT_ID}-sds-europe-west2-schema"
DATASET_ID = ""
SCHEMA_GUID = "UNASSIGNED"

if config.OAUTH_CLIENT_ID == "localhost":
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "sandbox-key.json"

# Set the subpath for the csv file with current timestamp if headless mode is enabled
if os.environ.get("LOCUST_HEADLESS") == "true":
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    subpath = timestamp + "/result"
    os.environ["LOCUST_CSV"] += subpath

# Initialize LocustHelper class
locust_helper = LocustHelper(BASE_URL, DATABASE_NAME, locust_test_id)


@events.init_command_line_parser.add_listener
def _(parser):
    # Add custom arguments to choose endpoints for testing
    parser.add_argument(
        "--test-endpoints",
        type=str,
        env_var="LOCUST_TEST_ENDPOINTS",
        choices=[
            "all",
            "exclude_post_schema",
            "post_schema",
            "get_unit_data",
            "get_dataset_metadata",
            "get_schema_metadata",
            "get_schema",
            "get_schema_v2",
            "get_survey_list",
        ],
        default="exclude_post_schema",
        help="Choose endpoints to test",
    )
    parser.add_argument(
        "--dataset_entries",
        type=int,
        env_var="LOCUST_DATASET_ENTRIES",
        default=1000,
        help="Number of unit data in the generated dataset between 10 to 90000",
    )


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """
    Function to run before the test starts
    """
    logger.info("Setting header for requests")
    global HEADER
    HEADER = locust_helper.set_header()

    if not isinstance(environment.runner, MasterRunner):
        # Worker Node operation

        # Get schema guid
        logger.info("Retrieving schema GUID")
        global SCHEMA_GUID
        SCHEMA_GUID = locust_helper.wait_and_get_schema_guid(HEADER)
        logger.info(f"Test schema GUID: {SCHEMA_GUID}")

        # Get dataset ID
        logger.info("Retrieving dataset ID")
        global DATASET_ID
        if config.OAUTH_CLIENT_ID == "localhost":
            DATASET_ID = locust_helper.get_dataset_id_from_local()
        else:
            DATASET_ID = locust_helper.get_dataset_id(HEADER, config.TEST_DATASET_FILE)
        logger.info(f"Test dataset ID: {DATASET_ID}")

        logger.info("Preparation for testing is complete. Test will be starting")

    else:
        # Master Node operation

        # Generate dataset file
        response = locust_helper.get_dataset_metadata(HEADER)

        if response.status_code == 404:
            logger.info("Master: Generating dataset file...")

            json_generator = JsonGenerator(
                locust_test_id,
                config.TEST_DATASET_FILE,
                config.FIXED_IDENTIFIERS,
            )

            json_generator.generate_dataset_file(
                environment.parsed_options.dataset_entries
            )

            # Publish 1 dataset for endpoint testing
            logger.info("Master: Publishing SDS dataset for testing...")
            locust_helper.create_dataset_record_before_test(config.TEST_DATASET_FILE)

        # Publish 1 schema for endpoint testing
        response = locust_helper.get_schema_metadata(HEADER)

        if response.status_code == 404:
            logger.info("Master: Publishing SDS schema for testing...")
            schema_payload = locust_helper.load_json(config.TEST_SCHEMA_FILE)
            locust_helper.create_schema_record_before_test(HEADER, schema_payload)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    Function to run after the test stops
    """
    """if not isinstance(environment.runner, MasterRunner):
        if config.OAUTH_CLIENT_ID == "localhost":
            # Delete generated dataset file
            locust_helper.delete_local_file(config.TEST_DATASET_FILE)
            logging.info("dataset file for publish is deleted")
        else:
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
            )"""


class PerformanceTests(FastHttpUser):
    wait_time = between(0.05, 0.1)
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
            self.environment.parsed_options.test_endpoints == "all"
            or self.environment.parsed_options.test_endpoints == "post_schema"
        ):
            self.client.post(
                f"{BASE_URL}/v1/schema?survey_id={locust_test_id}",
                json=self.post_sds_schema_payload,
                headers=HEADER,
            )
        else:
            pass

    # Test get schema metadata endpoint
    @task
    def http_get_sds_schema_metadata_v1(self):
        """Performance test task for the `http_get_sds_schema_metadata_v1` function"""
        if (
            self.environment.parsed_options.test_endpoints == "all"
            or self.environment.parsed_options.test_endpoints == "exclude_post_schema"
            or self.environment.parsed_options.test_endpoints == "get_schema_metadata"
        ):
            self.client.get(
                f"{BASE_URL}/v1/schema_metadata?survey_id={locust_test_id}",
                headers=HEADER,
            )
        else:
            pass

    # Test get schema endpoint
    @task
    def http_get_sds_schema_v1(self):
        """Performance test task for the `http_get_sds_schema_v1` function"""
        if (
            self.environment.parsed_options.test_endpoints == "all"
            or self.environment.parsed_options.test_endpoints == "exclude_post_schema"
            or self.environment.parsed_options.test_endpoints == "get_schema"
        ):
            self.client.get(
                f"{BASE_URL}/v1/schema?survey_id={locust_test_id}",
                headers=HEADER,
            )
        else:
            pass

    # Test get schema v2 endpoint
    @task
    def http_get_sds_schema_v2(self):
        """Performance test task for the `http_get_sds_schema_v2` function"""
        if (
            self.environment.parsed_options.test_endpoints == "all"
            or self.environment.parsed_options.test_endpoints == "exclude_post_schema"
            or self.environment.parsed_options.test_endpoints == "get_schema_v2"
        ):
            self.client.get(
                f"{BASE_URL}/v2/schema?guid={SCHEMA_GUID}",
                headers=HEADER,
            )
        else:
            pass

    # Test dataset metadata endpoint
    @task
    def http_get_sds_dataset_metadata_v1(self):
        """Performance test task for the `http_get_sds_dataset_metadata_v1` function"""
        if (
            self.environment.parsed_options.test_endpoints == "all"
            or self.environment.parsed_options.test_endpoints == "exclude_post_schema"
            or self.environment.parsed_options.test_endpoints == "get_dataset_metadata"
        ):
            self.client.get(
                f"{BASE_URL}/v1/dataset_metadata?survey_id={locust_test_id}&period_id={locust_test_id}",
                headers=HEADER,
            )
        else:
            pass

    # Test unit data endpoint
    @task
    def http_get_sds_unit_data_v1(self):
        """Performance test task for the `http_get_sds_unit_data_v1` function"""
        if (
            self.environment.parsed_options.test_endpoints == "all"
            or self.environment.parsed_options.test_endpoints == "exclude_post_schema"
            or self.environment.parsed_options.test_endpoints == "get_unit_data"
        ):
            self.client.get(
                f"{BASE_URL}/v1/unit_data?dataset_id={DATASET_ID}&identifier={TEST_UNIT_DATA_IDENTIFIER}",
                headers=HEADER,
            )

        else:
            pass

    # Test get survey list endpoint
    @task
    def http_get_sds_survey_list_v1(self):
        """Performance test task for the `http_get_sds_survey_list_v1` function"""
        if (
            self.environment.parsed_options.test_endpoints == "all"
            or self.environment.parsed_options.test_endpoints == "exclude_post_schema"
            or self.environment.parsed_options.test_endpoints == "get_survey_list"
        ):
            self.client.get(f"{BASE_URL}/v1/survey_list", headers=HEADER)
        else:
            pass
