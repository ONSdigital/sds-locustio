import datetime
import logging
import os
from http import HTTPStatus

from configs.config import config
from json_generator import JsonGenerator
from locust import FastHttpUser, between, events
from locust.runners import MasterRunner
from locust_helper import LocustHelper
from locust_test import FIXED_IDENTIFIERS, LOCUST_TEST_ID
from configs.endpoints_config import SDS_ENDPOINTS, SDS_ENDPOINTS_CHOICE, SDS_ENDPOINTS_DEFAULT
from configs.endpoints_helpers import EndpointsHelpers
from configs.runtime_config import RuntimeConfig

# Set up logging

logger = logging.getLogger(__name__)

# Set up runtime config to store runtime values that are needed across different test methods and processes

runtime_config = RuntimeConfig()

# Set the subpath for the csv file with current timestamp if headless mode is enabled
if os.environ.get("LOCUST_HEADLESS") == "true":
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    subpath = timestamp + "/result"
    os.environ["LOCUST_CSV"] = "/" + os.environ["LOCUST_CSV"] + subpath

# Initialize LocustHelper class
DATABASE_NAME = f"{config.PROJECT_ID}-{config.DATABASE}"
locust_helper = LocustHelper(config.BASE_URL, DATABASE_NAME, LOCUST_TEST_ID)


@events.init_command_line_parser.add_listener
def _(parser):
    # Add custom arguments to choose endpoints for testing
    parser.add_argument(
        "--test-endpoints",
        type=str,
        env_var="LOCUST_TEST_ENDPOINTS",
        choices= SDS_ENDPOINTS_CHOICE,
        default=SDS_ENDPOINTS_DEFAULT,
        help="Choose endpoints to test",
    )
    parser.add_argument(
        "--dataset_entries",
        type=int,
        env_var="LOCUST_DATASET_ENTRIES",
        default=1000,
        help="Number of unit data in the generated dataset between 10 to 90000",
    )


def run_master_test_start_process(header, environment):
    # Generate dataset file
    response = locust_helper.get_dataset_metadata(header)

    if response.status_code == HTTPStatus.NOT_FOUND:
        logger.info("Generating dataset file...")

        json_generator = JsonGenerator(
            LOCUST_TEST_ID,
            config.TEST_DATASET_FILE,
            FIXED_IDENTIFIERS,
        )

        json_generator.generate_dataset_file(environment.parsed_options.dataset_entries)

        # Publish 1 dataset for endpoint testing
        logger.info("Publishing SDS dataset for testing...")
        locust_helper.create_dataset_record_before_test(config.TEST_DATASET_FILE)

    # Publish 1 schema for endpoint testing
    response = locust_helper.get_schema_metadata(header)

    if response.status_code == HTTPStatus.NOT_FOUND:
        logger.info("Publishing SDS schema for testing...")
        schema_payload = locust_helper.load_json(config.TEST_SCHEMA_FILE)
        locust_helper.create_schema_record_before_test(header, schema_payload)


def run_worker_test_start_process(header):
    # Get schema guid
    logger.info("Retrieving schema GUID")
    runtime_config.SCHEMA_GUID = locust_helper.wait_and_get_schema_guid(header)
    logger.info(f"Test schema GUID: {runtime_config.SCHEMA_GUID}")

    # Get dataset ID
    logger.info("Retrieving dataset ID")
    runtime_config.DATASET_ID = locust_helper.get_dataset_id(header, config.TEST_DATASET_FILE)
    logger.info(f"Test dataset ID: {runtime_config.DATASET_ID}")

    logger.info("Preparation for testing is complete. Test will be starting")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """
    Function to run before the test starts
    """
    logger.info("Setting header for requests")
    runtime_config.HEADER = locust_helper.set_header()

    if os.environ.get("LOCUST_HEADLESS") == "true":
        if not isinstance(environment.runner, MasterRunner):
            # Worker Node operation
            run_worker_test_start_process(runtime_config.HEADER)

        else:
            # Master Node operation
            run_master_test_start_process(runtime_config.HEADER, environment)

    else:
        run_master_test_start_process(runtime_config.HEADER, environment)
        run_worker_test_start_process(runtime_config.HEADER)


class PerformanceTests(FastHttpUser):
    wait_time = between(0.05, 0.1)
    tasks = []
    host = config.BASE_URL
    endpoint_helpers: EndpointsHelpers

    def __init__(self, *args, **kwargs):
        """Override default init to save some additional class attributes"""
        super().__init__(*args, **kwargs)
        self.endpoint_helpers = EndpointsHelpers(config.BASE_URL, SDS_ENDPOINTS)

    def on_start(self):
        super().on_start()

    def on_stop(self):
        super().on_stop()


# Test creating dynamic tasks based on the chosen endpoints - example with get unit data endpoint
locust_test_methods = []
for endpoint_name in SDS_ENDPOINTS.keys():
    logger.info(f"Creating dynamic test method for endpoint: {endpoint_name}")
    # Closure function to create a test method for an endpoint
    def create_test_method(endpoint):
        def test_method(user):
            selected_endpoints = user.environment.parsed_options.test_endpoints

            if selected_endpoints not in ("all", endpoint):
                pass
            else:
                user.endpoint_helpers.send_request(
                    client=user.client,
                    endpoint_name=endpoint,
                    runtime_config=runtime_config,
                )

        return test_method

    locust_test_methods.append(create_test_method(endpoint_name))

# Add the created test methods to the tasks attribute of the PerformanceTests class
PerformanceTests.tasks = locust_test_methods
