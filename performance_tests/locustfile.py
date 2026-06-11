import datetime
import logging
import os

from configs.config import config, App
from locust import FastHttpUser, between, events
from locust_helper import LocustHelper
from configs.endpoints_config import (SDS_ENDPOINTS, CIR_ENDPOINTS, SDS_ENDPOINTS_CHOICE, CIR_ENDPOINTS_CHOICE,
                                      SDS_ENDPOINTS_DEFAULT, CIR_ENDPOINTS_DEFAULT, EndpointConfig)
from configs.endpoints_helpers import EndpointsHelpers
from configs.runtime_config import RuntimeConfig
from locust_tests_factory import LocustTestsFactory
from postprocess.postprocess_mapper import PostprocessMapper
from preprocess.preprocess_mapper import PreprocessMapper

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
locust_helper = LocustHelper()

if config.APP == App.SDS:
    TEST_ENDPOINTS = SDS_ENDPOINTS
    TEST_ENDPOINTS_CHOICE = SDS_ENDPOINTS_CHOICE
    TEST_ENDPOINTS_DEFAULT = SDS_ENDPOINTS_DEFAULT
elif config.APP == App.CIR:
    TEST_ENDPOINTS = CIR_ENDPOINTS
    TEST_ENDPOINTS_CHOICE = CIR_ENDPOINTS_CHOICE
    TEST_ENDPOINTS_DEFAULT = CIR_ENDPOINTS_DEFAULT


@events.init_command_line_parser.add_listener
def _(parser):
    # Add custom arguments to choose endpoints for testing
    parser.add_argument(
        "--test-endpoints",
        type=str,
        env_var="LOCUST_TEST_ENDPOINTS",
        choices= TEST_ENDPOINTS_CHOICE,
        default=TEST_ENDPOINTS_DEFAULT,
        help="Choose endpoints to test",
    )
    if config.APP == App.SDS:
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
    runtime_config.HEADER = locust_helper.set_header()

    preprocess_mapper = PreprocessMapper()

    preprocessors_required = preprocess_mapper.initiate_preprocessors(
        header=runtime_config.HEADER,
        environment=environment
    )

    for preprocessor in preprocessors_required:
        preprocessor.preprocess()

    runtime_config.set_config_from_preprocessors(preprocessors_required)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    Function to run after the test ends
    """
    logger.info("Test is stopping. Performing cleanup if necessary.")

    postprocess_mapper = PostprocessMapper()

    postprocess_required = postprocess_mapper.initiate_postprocessors(
        header=runtime_config.HEADER,
        environment=environment
    )

    for postprocessor in postprocess_required:
        postprocessor.postprocess()



class PerformanceTests(FastHttpUser):
    wait_time = between(0.05, 0.1)
    tasks = [] # Tasks will be populated dynamically at init
    host = config.BASE_URL # Required by Locust
    endpoint_configs: dict[str, EndpointConfig] # Endpoint configurations for the selected endpoints to be tested
    endpoint_helpers: EndpointsHelpers
    locust_tests_factory: LocustTestsFactory

    def __init__(self, *args, **kwargs):
        """Override default init to save some additional class attributes"""
        super().__init__(*args, **kwargs)

        # Define endpoints to be tested
        self.endpoint_helpers = EndpointsHelpers(config.BASE_URL, TEST_ENDPOINTS)
        self.endpoint_configs = self.endpoint_helpers.get_endpoint_configs_from_selection(
            [self.environment.parsed_options.test_endpoints]
        )

        # Populate tasks
        self.locust_tests_factory = LocustTestsFactory(self.endpoint_configs)
        self.tasks = self.locust_tests_factory.populate_locust_tasks(runtime_config)

    def on_start(self):
        super().on_start()

    def on_stop(self):
        super().on_stop()
