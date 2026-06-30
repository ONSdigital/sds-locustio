import logging
from collections.abc import Callable
from typing import Final

import gevent
from locust import FastHttpUser, between, events
from locust.env import Environment
from locust.runners import MasterRunner

from performance_tests.configs.config import App, config
from performance_tests.configs.endpoints_config import ENDPOINTS_CONFIG, EndpointConfig
from performance_tests.configs.endpoints_helpers import EndpointsHelpers
from performance_tests.configs.runtime_config import RuntimeConfig
from performance_tests.locust_helper import LocustHelper
from performance_tests.locust_tests_factory import LocustTestsFactory
from performance_tests.postprocess.postprocess_mapper import PostprocessMapper
from performance_tests.preprocess.preprocess_mapper import PreprocessMapper

logger = logging.getLogger(__name__)

# Set test endpoints
TEST_ENDPOINTS_CONFIG: Final[dict] = ENDPOINTS_CONFIG.get(config.APP)

# Set up runtime config to store runtime values that are needed across different test methods and processes
runtime_config: RuntimeConfig = RuntimeConfig()

# Initialize LocustHelper class
locust_helper: LocustHelper = LocustHelper()

# Set the path for CSV result files for headless mode.
locust_helper.set_csv_result_path()


@events.init_command_line_parser.add_listener
def _(parser):
    # Add custom arguments to choose endpoints for testing
    parser.add_argument(
        "--test-endpoints",
        type=str,
        env_var="LOCUST_TEST_ENDPOINTS",
        choices= TEST_ENDPOINTS_CONFIG["test_endpoints_choice"],
        default=TEST_ENDPOINTS_CONFIG["test_endpoints_default"],
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
def on_test_start(environment: Environment, **kwargs):
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


@events.quitting.add_listener
def on_test_quitting(environment: Environment, **kwargs):
    """
    Function to run after the test ends, just before the program quits. This is a replacement of the previous
    on_stop event hook to ensure it runs after all worker nodes have definitely stopped
    """
    logger.info("Program is quitting...")

    postprocess_mapper = PostprocessMapper()

    postprocess_required = postprocess_mapper.initiate_postprocessors(
        header=runtime_config.HEADER,
        environment=environment
    )

    # If master node, wait for all users to finish executing before proceeding with post-processing
    if not config.HEADLESS_MODE or isinstance(environment.runner, MasterRunner):
        while environment.runner.user_count > 0:
            gevent.sleep(0.5)

    logger.info("All users have finished executing. Proceeding with post-processing.")

    for postprocessor in postprocess_required:
        postprocessor.postprocess()


class PerformanceTests(FastHttpUser):
    wait_time: float = between(0.05, 0.1)
    tasks: list[Callable] | None = None # Tasks will be populated dynamically
    host: str = config.BASE_URL # Required by Locust
    endpoint_configs: dict[str, EndpointConfig] # Endpoint configurations for the selected endpoints to be tested
    endpoint_helpers: EndpointsHelpers
    locust_tests_factory: LocustTestsFactory

    def __init__(self, *args, **kwargs):
        """Override default init to save some additional class attributes"""
        super().__init__(*args, **kwargs)

        # Define endpoints to be tested
        self.endpoint_helpers = EndpointsHelpers(config.BASE_URL, TEST_ENDPOINTS_CONFIG["test_endpoints"])
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
