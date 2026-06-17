import logging

from configs.endpoints_config import EndpointConfig
from configs.runtime_config import RuntimeConfig

logger = logging.getLogger(__name__)


class LocustTestsFactory:
    def __init__(self, endpoint_configs: dict[str, EndpointConfig]):
        self.endpoint_configs = endpoint_configs

    def populate_locust_tasks(self, runtime_config: RuntimeConfig) -> list:
        locust_tasks = []
        for endpoint_name in self.endpoint_configs.keys():
            logger.info(f"Creating test method for endpoint: {endpoint_name}")

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

            locust_tasks.append(create_test_method(endpoint_name))

        return locust_tasks
